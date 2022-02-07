"""""""""
Written by Mengzhan Liufu at Yu Lab, University of Chicago
"""""""""

import math
from bandpass_filter import bandpass_filter


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


def detect_with_rms(buffer, sampling_freq, target_lowcut, target_highcut, threshold):
    """
    :param buffer: the buffer of data
    :param sampling_freq: data sampling rate
    :param target_lowcut: the lower bound of target frequency range
    :param target_highcut: the higher bound of target frequency range
    :param threshold: the threshold of power for making decision/judgement

    :return: whether the activity in freq range [low_cut, high_cut] crosses threshold
    :rtype: boolean
    """

    current_rms = calculate_rms(bandpass_filter('butterworth', buffer, sampling_freq, 1, \
                                                   target_lowcut, target_highcut))
    return current_rms >= threshold