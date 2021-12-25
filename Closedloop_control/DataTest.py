import trodes_connection as tc
import rms_detection as rd
import lfp_buffering as lb
from collections import deque
import threading
import time


trodes_py = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20)
trodes_client = trodes_py[0]
trodes_hardware = trodes_py[1]
trodes_info = trodes_py[2]
lfp_sampling_rate = trodes_py[3]
lfp_sampling_period = trodes_py[4]
start_time = 0
print('Connection established')

def bandpass_filter(filter_name, flattened_array, sampling_freq, order, lowcut, highcut):
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

channeldata =[]
while True:
    current_sample = trodes_client.receive()
    current_data = current_sample['lfpData']
    print(current_data)
    channeldata.append(current_data[0])
    print(channeldata)
    
    filtered_data = bandpass_filter('butterworth', channeldata, lfp_sampling_rate, 1, 4, 10)
    
    if filtered_data<50:
        print ('yes')


	