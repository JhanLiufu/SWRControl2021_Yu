"""""""""
Written by Mengzhan Liufu at Yu Lab, the University of Chicago, November 2021
"""""""""

from bandpass_filter import bandpass_filter
import numpy as np


def calculate_noise(filter_type, flattened_array, sampling_rate, order, lowcut, highcut, current_sample):
    '''
    Filter to [lowcut, highcut] range and return the value at current sample

    :param filter_type:
    :param flattened_array:
    :param sampling_rate:
    :param order:
    :param lowcut:
    :param highcut:
    :param current_sample:
    :return current_noise_data[-1]: current power in [lowcut, highcut] range
    '''

    current_noise_data = bandpass_filter(filter_type, np.append(flattened_array, current_sample), \
                                          sampling_rate, order, lowcut, highcut)
    '''
    The reason for np.append(flattened——array, current_sample) is that directly appending current_sample to the input
    buffer would really change the buffer (python lists are mutable). np.append(), on the other hand, returns a new 
    array that has nothing to do with the input data_buffer. Alternatively, we can copy data_buffer to a new list first
    and append to that copy. Not sure which way's faster
    '''
    return abs(current_noise_data[-1])  # return absolute value here


def data_buffering(buffer_pool, client, buffer, buffer_size, sampling_freq, noise_lowcut, noise_highcut, noise_threshold, *channel):
    """
    Receive lfp data, determine whether influenced by global noise, then update data_buffer accordingly

    :param client: trodes client object
    :param buffer: the real-time updating buffer queue
    :param buffer_size: the length of buffers for real-time processing
    :param sampling_freq: data sampling rate
    :param noise_lowcut: the lower bound of noise (usually a high freq band of no biological events)
    :param noise_highcut: the higher bound of noise (usually a high freq band of no biological events)
    :param noise_threshold: if the power in noise range exceeds this value, current sample is global noise
    :param buffer_pool: multiprocessing Pool object
    :param channel: unknown number of channel aliases
    """
    if len(buffer) != len(channel):
        raise ValueError('Number of channels should be consistent')
    if len(buffer[0]) != buffer_size:
        raise ValueError('Buffer size should be consistent')

    while True:
        # receive the latest sample sent by trodes server
        current_sample = client.receive()
        current_data = current_sample['lfpData']

        # parallelize calculation for each channel to parallel processes
        result_objects = [buffer_pool.apply_async(calculate_noise, \
                                                  args=('butterworth', buffer[i], sampling_freq, 1, \
                                                  noise_lowcut, noise_highcut, current_data[channel[i]])) \
                                                  for i in range(len(channel))]
        '''
        result_objects is a list of result objects returned by apply_async(). They are objects, not numbers. The r.get()
        functions below get the numbers out of the objects and put them in a list. np.mean() then finds average. 
        Alternatively, apply_async() can take a callback function as input to transfer results. Not sure which way's
        faster
        '''
        # calculate average power in noise range across channels and determine noisy or not
        buffer_decision = np.mean([r.get() for r in result_objects]) > noise_threshold

        print('Current noise-decision:')
        print(buffer_decision)
        print('\n')

        if buffer_decision:
            continue

        # append new data to buffer and pop the least recent one
        '''
        If this takes too long, try to integrate this into multiprocessing
        '''
        for i in range(len(channel)):
            buffer[i].append(current_data[channel[i]])
            buffer[i].pop(0)