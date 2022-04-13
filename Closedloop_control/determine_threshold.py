"""""""""
Written by Mengzhan Liufu at Yu Lab, University of Chicago
"""""""""

from bandpass_filter import bandpass_filter
import numpy as np
from rms_detection import calculate_rms


def determine_threshold(client, sampling_freq, target_lowcut, target_highcut, noise_lowcut, noise_highcut, target_numstd, \
                        noise_numstd, initial_length, buffer_size):

    initial_data = []
    for i in range(0, initial_length):
        current_sample = client.receive()
        current_data = current_sample['lfpData']
        initial_data.append(current_data[3])

    initial_data = np.array(initial_data)

    target_range_data = bandpass_filter('butterworth', initial_data, sampling_freq, 1, target_lowcut, target_highcut)
    noise_range_data = np.abs(bandpass_filter('butterworth', initial_data, sampling_freq, 1, noise_lowcut, noise_highcut))

    noise_threshold = np.mean(noise_range_data) + noise_numstd*np.std(noise_range_data)

    target_denoised = target_range_data[noise_range_data < noise_threshold]
    target_denoised = np.array(target_denoised)

    return 300, 1000, target_denoised[len(target_denoised) - buffer_size:].tolist()

