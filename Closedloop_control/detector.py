'''
Written by Mengzhan Liufu at Yu Lab, University of Chicago
'''
from collections import deque
import numpy as np
import math
from scipy.signal import sosfiltfilt


class Detector:

    def __init__(self, num_to_wait, buffer_size, freq_lowcut, freq_highcut, noise_lowcut, noise_highcut, stim_num_std,
                 noise_num_std, target_channel, stim_threshold=300, noise_threshold=1000, sampling_rate=1500):
        # the default value of stim_threshold and noise_threshold should be known empirically
        self.decision_buffer = deque([False]*num_to_wait, maxlen=num_to_wait)
        self.stim_status = False
        # previously 15, but no decision made. Maybe 15 * (~20ms) might be too long?
        self.buffer_size = buffer_size
        self.data_buffer = deque([], maxlen=buffer_size)
        self.freq_lowcut = freq_lowcut
        # low bound of target frequency range
        self.freq_highcut = freq_highcut
        # high bound of target frequency range
        self.noise_lowcut = noise_lowcut
        # low bound of noise range (usually a high freq band)
        self.noie_highcut = noise_highcut
        # high bound of noise range
        self.stim_num_std = stim_num_std
        self.noise_num_std = noise_num_std
        self.target_channel = target_channel
        self.stim_threshold = stim_threshold
        self.noise_threshold = noise_threshold
        # make this value high; filtered data is spiky on the edges
        self.sampling_rate = sampling_rate
        self.filter = None

    def decide_stim(self):
        curr_rms = math.sqrt(np.mean(np.square(sosfiltfilt(self.filter, self.data_buffer))))
        time.sleep(0.0000005)
        self.decision_buffer.append(curr_rms >= self.stim_threshold)
        return all(self.decision_buffer)

    def flip_stim_status(self):
        self.stim_status = not self.stim_status