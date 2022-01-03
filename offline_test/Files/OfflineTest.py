"""""""""
Written by Mengzhan Liufu and Sameera Shridhar at Yu Lab, the University of Chicago, November 2021
"""""""""

import readTrodesExtractedDataFile3 as TrodesReader
from collections import deque
import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt


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
    filtered_buffer = bandpass_filter('butterworth', buffer, lfp_sampling_rate, 0, low_cut, high_cut)
    current_rms = calculate_rms(filtered_buffer)
    print(current_rms)
    if current_rms >= threshold:
        return True
    else:
        return False


lfp_sampling_rate = 1250
lfp_sampling_period = (1/1250)*(10**9)
fNQ = 600

data_path = r'C:\Users\John LauFoo\Box\Jhan\ClosedLoopControl Project\DATA\20211117_testing_5min\20211117_testing_5min.LFP\20211117_testing_5min.LFP_nt28ch1.dat'
timestamp_path = r'C:\Users\John LauFoo\Box\Jhan\ClosedLoopControl Project\DATA\20211117_testing_5min\20211117_testing_5min.LFP\20211117_testing_5min.timestamps.dat'

data = TrodesReader.readTrodesExtractedDataFile(data_path)
timestamps = TrodesReader.readTrodesExtractedDataFile(timestamp_path)

lfp_data = []
for i in data['data']:
    lfp_data.append(i[0])

ripple_range_filtered_data = bandpass_filter('butterworth', lfp_data, lfp_sampling_rate, 0, 140, 225)
sharp_wave_range_filtered_data = bandpass_filter('butterworth', lfp_data, lfp_sampling_rate, 0, 5, 15)
gamma_range_filtered_data = bandpass_filter('butterworth', lfp_data, lfp_sampling_rate, 0, 20, 40)

ripple_rms_history = []
sharp_wave_rms_history = []
gamma_rms_history = []
for i in range(2499, len(ripple_range_filtered_data)):
    ripple_buffer = ripple_range_filtered_data[i-2499:i]
    ripple_rms_history.append(calculate_rms(ripple_buffer))
    sharp_wave_buffer = sharp_wave_range_filtered_data[i-2499:i]
    sharp_wave_rms_history.append(calculate_rms(sharp_wave_buffer))
    gamma_range_buffer = gamma_range_filtered_data[i-2499:i]
    gamma_rms_history.append(calculate_rms(gamma_range_buffer))

ripple_avg_rms = sum(ripple_rms_history)/len(ripple_rms_history)
sharp_wave_avg_rms = sum(sharp_wave_rms_history)/len(sharp_wave_rms_history)
plt.style.use('seaborn-white')
#plt.plot(rms_history)
#plt.show()
