"""""""""
Written by Mengzhan Liufu at Yu Lab, University of Chicago
"""""""""

from bandpass_filter import bandpass_filter
import numpy as np
from rms_detection import calculate_rms
'''
Although the analysis in determine_threshold is not time critical, since we are using part of target_denoised to 
initialize data_buffer, the analysis here should also be as fast as possible.
'''


def determine_threshold(Pool, client, sampling_freq, target_lowcut, target_highcut, noise_lowcut, noise_highcut, target_numstd, \
                        noise_numstd, initial_length, buffer_size, *channel):
    '''
    Determine target range threshold and global noise threshold for online deteection
    :param client: socket subscriber object
    :param sampling_freq: data sampling rate
    :param target_lowcut: the low bound of target frequency range
    :param target_highcut: the high bound of target frequency range
    :param noise_lowcut: the low bound of noise frequency range (usually a high frequency range)
    :param noise_highcut: the high bound of noise frequency range
    :param target_numstd: # of standard deviation above average for target freq range
    :param noise_numstd:
    :param initial_length: # of samples used for threshold determination
    :param buffer_size: # of samples in buffer
    :param Pool: multiprocessing Pool object
    :param channel: unknown number of channel aliases

    :return target_threshold
    :return noise_threshold
    :return target_denoised[:][len(initial_length)-buffer_size:]: initial data_buffer of size len(channel)xbuffer_size
    '''

    # acquire raw data in initial period
    initial_data = np.zeros((len(channel), initial_length), dtype=float)
    for i in range(0, initial_length):
        current_sample = client.receive()
        current_data = current_sample['lfpData']
        for j in range(len(channel)):
            initial_data[j, i] = current_data[channel[j]]

    print('Initial-period Raw data:')
    print(initial_data)
    print('\n')

    # store target range data and noise range data separately
    target_results = [Pool.apply_async(bandpass_filter, args=('butterworth', np.array(initial_data[i, :]), sampling_freq, \
                                                              1, target_lowcut, target_highcut)) for i in range(len(channel))]
    target_range_data = np.array([tr.get() for tr in target_results])
    noise_results = [Pool.apply_async(bandpass_filter, args=('butterworth', np.array(initial_data[i, :]), sampling_freq, \
                                                              1, noise_lowcut, noise_highcut)) for i in range(len(channel))]
    noise_range_data = np.abs([nr.get() for nr in noise_results])  # this should actually have signal.hilbert() but

    # determine noise threshold
    noise_range_avg = np.average(noise_range_data, axis=0)
    noise_threshold = np.mean(noise_range_avg) + noise_numstd*np.std(noise_range_avg)

    print('Initial-period Noise range:')
    print(noise_range_data)
    print('\n')
    print('Initial-period Noise range averaged:')
    print(noise_range_avg)
    print('\n')
    print('Initial-period Noise range avg:')
    print(np.mean(noise_range_avg))
    print('\n')
    print('Initial-period Noise range std:')
    print(np.std(noise_range_avg))
    print('\n')

    # denoise target range data
    '''
    actually should have another condition here (target power < 1000) to make sure that the noise edges
    are removed too. But then the length of each row is not guaranteed to be the same, which prevents
    us from averaging them. Need to solve this because the noise edges (as we've seen in offline analysis)
    have high power too
    '''
    target_denoised = [target_range_data[i, :][noise_range_avg < noise_threshold] for i in range(len(channel))]
    target_denoised = np.array(target_denoised)
    # determine target range threshold with denoised data
    target_denoised_avg = np.average(target_denoised, axis=0)
    '''
    The stepwise calculate_rms() here will take a lot of time. Tried multiprocessing it, but calculate_rms() somehow
    doesn't work with array segments in multiprocessing framework. Need to solve this!
    '''
    initial_rms_avg = [calculate_rms(target_denoised_avg[i-buffer_size:i]) \
                       for i in range(buffer_size, len(target_denoised_avg))]

    print('Target range data (not denoised):')
    print(target_range_data)
    print('\n')
    print('Target range data (denoised):')
    print(target_denoised)
    print('\n')
    print('Target range data avg (denoised)')
    print(target_denoised_avg)
    print('\n')
    print('Initial-period RMS avg:')
    print(np.mean(initial_rms_avg))
    print('\n')
    print('Initial-period RMS std:')
    print(np.std(initial_rms_avg))
    print('\n')

    target_threshold = np.mean(initial_rms_avg) + target_numstd*np.std(initial_rms_avg)

    # return the noise and target range thresholds and initial data_buffer
    return target_threshold, noise_threshold, target_denoised[:,  len(target_denoised_avg)-buffer_size:].tolist()


