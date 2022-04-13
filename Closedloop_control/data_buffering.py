'''
Written by Mengzhan Liufu at Yu Lab, University of Chicago, November 2021
'''
import numpy as np


# def calculate_noise(filter_type, flattened_array, sampling_rate, order, lowcut, highcut, current_sample):
#     current_noise_data = bandpass_filter(filter_type, np.append(flattened_array, current_sample), \
#                                           sampling_rate, order, lowcut, highcut)
#
#     return abs(current_noise_data[-1])  # return absolute value here


def data_buffering(client, Detector):

    while True:
        current_data = client.receive()['lfpData']
        Detector.data_buffer.append(current_data[Detector.target_channel])

