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
target_threshold = 300  # default target range detection threshold (refer to offline analysis!)
noise_threshold = 300  # default noise range detection threshold

# Determine threshold
# the number and aliases of channels input here should be exactly the same as those for data_buffering()
if __name__ == '__main__':
    my_pool = mp.Pool(mp.cpu_count())
    target_threshold, noise_threshold, data_buffer = determine_threshold(my_pool, trodes_client, sampling_rate, frequency_lowcut, \
                                                                         frequency_highcut, noise_lowcut, noise_highcut, \
                                                                         stimulation_num_std, noise_num_std, 45000, buffer_size, \
                                                                         0, 2, 3)
print('Target range threshold:')
print(target_threshold)
print('Noise range threshold:')
print(noise_threshold)
print('\n')

# Start data buffering
buffering_thread = threading.Thread(target=data_buffering, args=(my_pool, trodes_client, data_buffer, buffer_size, sampling_rate, \
                                                                     noise_lowcut, noise_highcut, noise_threshold, \
                                                                     0, 2, 3))
buffering_thread.start()

# Start detecting
stimulation_status = False
decision_list = [False] * stimulation_num_wait

while True:
    print('Curren data buffer: ')
    print(data_buffer[0][:10])
    print('\n')

    decision_list.append(detect_with_rms(data_buffer, sampling_rate, frequency_lowcut, \
                                         frequency_highcut, target_threshold, my_pool))
    decision_list.pop(0)
    stimulation = True
    for m in decision_list:
        if not m:
            stimulation = False

    # print(stimulation)
    if (stimulation_status is False) and (stimulation is True):
        # tc.call_statescript(trodes_hardware, 1)
        print('Turn On')
        stimulation_status = True

    if (stimulation_status is True) and (stimulation is False):
        # tc.call_statescript(trodes_hardware, 2)
        print('Turn Off')
        stimulation_status = False

        '''
        Potential issue: multiprocessing module not termintaed properly. Should use pool.close() and pool.join()
        '''