"""""""""
Written by Mengzhan Liufu at Yu Lab, the University of Chicago, November 2021
"""""""""

from numpy import fft
import bandpass_filter as bpf
import numpy as np


def detection_with_fft(buffer, fNQ, low_cut, high_cut, lfp_sampling_period, lfp_sampling_rate, threshold):
    """
    :param buffer: the buffer of lfp data at current iteration
    :param fNQ: Nyquist frequency for filtering
    :param low_cut: the lower bound of the frequency band of interest
    :param high_cut: the upper bound of the frequency band of interest
    :param lfp_sampling_period: the period of lfp subscriber (time btw two packages sent)
    :param lfp_sampling_rate: the inverse of lfp_sampling_period
    :param threshold: the threshold of power for making decision/judgement

    :return: a dictionary containing the frequency axis and its corresponding power spectrum
    :rtype: dictionary
    """
    filtered_buffer = bpf.bandpass_filter('butterworth', buffer, lfp_sampling_rate, 1, 1, fNQ)
    freq_axis = fft.fftfreq(len(buffer), lfp_sampling_period)
    mask = []
    for m in freq_axis:
        if m >= 0:
            mask.append(m)

    fft_vals = fft.fft(filtered_buffer, n=len(mask))
    fft_real = (2.0/len(buffer))*np.abs(fft_vals)

    return {"fft_real": fft_real, "freq_axis": freq_axis}