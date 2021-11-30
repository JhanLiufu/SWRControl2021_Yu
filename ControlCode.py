"""""""""
Written by Mengzhan Liufu and Sameera Shridhar at Yu Lab, the University of Chicago, November 2021
"""""""""

#@timestamp: the Unix time accessed from local Windows
#@local_server_address: the TCP address of trodes server
#@lfp: the LFP data subscriber
#@lfpdata: the real time dictionary streamed from trodes

from trodesnetwork import trodes
from trodesnetwork import socket
from scipy import signal
import numpy as np
from numpy import fft
from collections import deque
import math
import threading

#global lfp_sampling_rate
lfp_sampling_rate = 1250
lfp_sampling_period = (1/1250)*(10**9)
fNQ = 600
#global start_time
start_time = 0

def connect_to_trodes(local_server_address, count_per_lfp):
    """
    Connect python client to trodes, get hardware sampling rate and calculate lfp sampling rate
    :param local_server_address:
    :param count_per_lfp:
    :return: lfp subscriber object
    :rtype: object
    """
    client = subscribe_to_lfp(local_server_address)
    info = get_trodes_info(local_server_address)
    global lfp_sampling_rate
    lfp_sampling_rate = info.request_timerate() / count_per_lfp
    global lfp_sampling_period
    lfp_sampling_period = (1 / lfp_sampling_rate) * (10 ** 9) #convert to nanoseconds

    return client


def bandpass_filter(filter_name, flattened_array, sampling_freq, order, lowcut, highcut):
    """
    Return a dictionary of filtered lfp data

    :param filter_name: name of the filter you want to use
    :type filter_name: string
    :param flattened_array: array of the raw lfp data
    :type flattened_array: np array
    :param sampling_freq: frequency lfp data was sampled at
    :type sampling_freq: int
    :param order: order of filter
    :type order: int
    :param lowcut: lower border of frequencies allowed to pass
    :type lowcut: int
    :param highcut: upper border of frequencies allowed to pass
    :type highcut: int

    :return: filtered lfp data
    :rtype: np array
    """
    if filter_name == 'elliptical':
        sos = signal.ellip(order, 0.01, 120, [lowcut, highcut], btype='bp', output='sos', fs=sampling_freq)
    if filter_name == 'butterworth':
        sos = signal.butter(order, [lowcut, highcut], 'bp', fs=sampling_freq, output='sos')
    if filter_name == 'cheby1':
        sos = signal.cheby1(order, 1, [lowcut, highcut], 'bp', fs=sampling_freq, output='sos')
    if filter_name == 'cheby2':
        sos = signal.cheby2(order, 15, [lowcut, highcut], 'bp', fs=sampling_freq, output='sos')

    y = signal.sosfiltfilt(sos, flattened_array)

    return y


def subscribe_to_lfp(local_server_address):
    """
    Return a trodes.socket subscriber to LFP data

    :param local_server_address: tcp server address of trodes

    :return: channel data
    :rtype: list, each element is of type int corresponding to each data channel
    """
    return socket.SourceSubscriber('source.lfp', server_address=local_server_address)


def get_trodes_info(local_server_address):
    """
    :param local_server_address:

    :return: TrodesInfoRequester Object
    :rtype: object
    """
    return trodes.TrodesInfoRequester(server_address=local_server_address)


def get_trodes_hardware(local_server_address):
    """
    :param local_server_address:

    :return: TrodesHardware Object
    :rtype: object
    """
    return trodes.TrodesHardware(server_address=local_server_address)


def calculate_rms(buffer):
    """
    return the root mean-squared of a given array
    :param buffer: any array or list of number

    :return: the root mean-squared value of the array as a proxy for its power
    :rtype: float
    """
    square_summed = 0
    for k in buffer:
        square_summed += (k**2)

    return math.sqrt(square_summed/len(buffer))


def detection_with_rms(buffer, low_cut, high_cut, threshold):
    """
    :param buffer: the buffer of lfp data at current iteration
    :param low_cut: the lower bound of the frequency band of interest
    :param high_cut: the upper bound of the frequency band of interest
    :param threshold: the threshold of power for making decision/judgement

    :return: whether there is activity in freq range [low_cut, high_cut] or not
    :rtype: boolean
    """
    filtered_buffer = bandpass_filter('butterworth', buffer, lfp_sampling_rate, 1, low_cut, high_cut)
    current_rms = calculate_rms(filtered_buffer)
    if current_rms >= threshold:
        return True
    else:
        return False


def detection_with_fft(buffer, fNQ, low_cut, high_cut, threshold):
    """
    :param buffer: the buffer of lfp data at current iteration
    :param fNQ: Nyquist frequency for filtering
    :param low_cut: the lower bound of the frequency band of interest
    :param high_cut: the upper bound of the frequency band of interest
    :param threshold: the threshold of power for making decision/judgement

    :return: a dictionary containing the frequency axis and its corresponding power spectrum
    :rtype: dictionary
    """
    filtered_buffer = bandpass_filter('butterworth', buffer, lfp_sampling_rate, 0, 1, fNQ)
    freq_axis = fft.fftfreq(len(buffer), lfp_sampling_period)
    mask = []
    for m in freq_axis:
        if m >= 0:
            mask.append(m)

    fft_vals = fft.fft(filtered_buffer, n=len(mask))
    fft_real = (2.0/len(buffer))*np.abs(fft_vals)

    return {"fft_real": fft_real, "freq_axis": freq_axis}


def set_start_time(start):
    global start_time
    start_time = start


def lfp_buffering():
    counter = 0
    while True:
        current_sample = trodes_client.receive()
        current_time = current_sample['systemTimestamp']
        current_data = current_sample['lfpData']
        lfp_buffer.append(current_data[0])

        if counter == 0:
            set_start_time(current_time)

        if counter < 500:
            counter = counter + 1
            continue

        lfp_buffer.popleft()  # discards the least recent data point


trodes_client = connect_to_trodes("tcp://127.0.0.1:49152", 20)
lfp_buffer = deque()
decision_list = [False, False, False]

buffering_thread = threading.Thread(target=lfp_buffering)
buffering_thread.start()

while True:

    if len(lfp_buffer) < 500:
        continue

    decision_list.append(detection_with_rms(lfp_buffer, 8, 12, 400))

    stimulation = True
    for m in range(len(decision_list)-3, len(decision_list)):
        if not decision_list[m]:
            stimulation = False

    print(stimulation)

