"""""""""
Written by Mengzhan Liufu at Yu Lab, University of Chicago
"""""""""

from bandpass_filter import bandpass_filter
import numpy as np
from scipy import signal

'''
Although the analysis in determine_threshold is not time critical, since we are using part of target_denoised to 
initialize data_buffer, the analysis here should also be as fast as possible.
'''


def determine_threshold(client, sampling_freq, target_lowcut, target_highcut, noise_lowcut, noise_highcut, target_numstd, \
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
    :param channel: unknown number of channel aliases

    :return target_threshold
    :return noise_threshold
    :return target_denoised[:][len(initial_length)-buffer_size:]: initial data_buffer of size len(channel)xbuffer_size
    '''

    # raw data in initial period
    initial_data = np.zeros(len(channel), initial_length)
    for i in range(0, initial_length):
        current_sample = client.receive()
        current_data = current_sample['lfpData']
        for j in range(len(channel)):
            initial_data[j, i] = current_data[channel[j]]

    # store target range data and noise range data separately
    target_range_data = np.zeros(len(channel), initial_length)
    noise_range_data = np.zeros(len(channel), initial_length)

    # filter to target range and noise range for each channel
    for i in range(len(channel)):
        target_range_data[i, :] = np.array(bandpass_filter('butterworth', np.array(initial_data[i, :]), sampling_freq, 1, \
                                                         target_lowcut, target_highcut))
        noise_range_data[i, :] = np.array(bandpass_filter('butterworth', np.array(initial_data[i, :]), sampling_freq, 1, \
                                                         noise_lowcut, noise_highcut))

    # determine noise threshold
    '''
    Need faster way of calculating average of noise range data among channels
    '''
    noise_range_avg = np.zeros(initial_length)
    for i in range(len(channel)):
        noise_range_avg += np.abs(signal.hilbert(np.array(noise_range_data[i, :])))
    noise_range_avg /= len(channel)
    noise_threshold = np.mean(noise_range_avg) + noise_numstd*np.std(noise_range_avg)

    # denoise target range data
    target_denoised = []
    '''
    The reason this is a 1D list rather than 2D target_denoied = [[]]*len(channel) is that somehow in 2D list if you 
    append to one row, that value also get appended to other rows (at least for initially empty lists). Working with
    2D list is better, then we don't need to do reshape() and tolist() later to convert np.array() back to list
    '''
    for i in range(len(channel)):
        for j in range(initial_length):
            if noise_range_avg[j] < noise_threshold:
                '''
                actually should have another condition here (target power < 1000) to make sure that the noise edges
                are removed too. But then the length of each row is not guaranteed to be the same, which prevents
                us from averaging them. Need to solve this because the noise edges (as we've seen in offline analysis)
                have high power too
                '''
                target_denoised.append(target_range_data[i])
    target_denoised = np.array(target_denoised).reshape(len(channel), initial_length).tolist()
    '''
    Numpy arrays don't have append() feature. Part of target_denoised will be returned to initialize data_buffer, and 
    we need to append samples to data_buffer(). 
    '''

    # determine target range threshold with denoised data
    '''
    Need faster way of calculating average of noise range data among channels
    '''
    target_denoised_avg = np.zeros(initial_length)
    for i in range(len(channel)):
        target_denoised_avg += target_denoised[i, :]
    target_threshold = np.mean(target_denoised) + target_numstd*np.std(target_denoised)

    # return the noise and target range thresholds and initial data_buffer
    '''
    The reason we are returning an initial buffer here is that the data_buffering() module needs to do online
    denoising, which means it needs to run bandpass_filter(), which can't be applied to an empty list
    '''
    return target_threshold, noise_threshold, target_denoised[:][len(initial_length)-buffer_size:]


