"""""""""
Written by Mengzhan Liufu at Yu Lab, University of Chicago
"""""""""

import trodes_connection as tc
from rms_detection import detect_with_rms
from data_buffering import data_buffering
from determine_threshold import determine_threshold
import threading
import multiprocessing as mp

# Connect to trodes
trodes_client, trodes_hardware, trodes_info, sampling_rate = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20, 'lfp')

# Parameters
stimulation_num_wait = 15
buffer_size = 150
frequency_lowcut = 140  # low bound of target frequency range
frequency_highcut = 250  # high bound of target frequency range
noise_lowcut = 500  # low bound of noise range (usually a high freq band)
noise_highcut = 600  # high bound of noise range
stimulation_num_std = 3
noise_num_std = 6  # make this value high; filtered data is spiky on the edges

# Determine threshold
# the number and aliases of channels input here should be exactly the same as those for data_buffering()
# lists and dicts are mutable types, tuples and numbers are not
target_threshold, noise_threshold, data_buffer = determine_threshold(trodes_client, sampling_rate, frequency_lowcut, \
                                                                     frequency_highcut, noise_lowcut, noise_highcut, \
                                                                     stimulation_num_std, noise_num_std, 45000, 0, 1, 2)

# Start data buffering
if __name__ == '__main__':
    my_pool = mp.Pool(mp.cpu_count())
    buffering_thread = threading.Thread(target=data_buffering, args=(trodes_client, data_buffer, buffer_size, \
                                                                     noise_lowcut, noise_highcut, noise_threshold, \
                                                                     my_pool, 0, 1, 2))
    buffering_thread.start()

stimulation_status = False
decision_list = [False] * stimulation_num_wait

# Start detecting
while True:
    decision_list.append(detect_with_rms(data_buffer, sampling_rate, frequency_lowcut, \
                                         frequency_highcut, target_threshold, my_pool))
    decision_list.pop(0)
    stimulation = True
    for m in decision_list:
        if not m:
            stimulation = False

    if (stimulation_status is False) and (stimulation is True):
        tc.call_statescript(trodes_hardware, 1)
        stimulation_status = True

    if (stimulation_status is True) and (stimulation is False):
        tc.call_statescript(trodes_hardware, 2)
        stimulation_status = False

        '''
        Potential issue: multiprocessing module not termintaed properly. Should use pool.close() and pool.join()
        '''