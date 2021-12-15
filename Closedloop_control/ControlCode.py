import trodes_connection as tc
import rms_detection as rd
import lfp_buffering as lb
from collections import deque
import threading
import time


trodes_py = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20)
trodes_client = trodes_py[0]
trodes_hardware = trodes_py[1]
trodes_info = trodes_py[2]
lfp_sampling_rate = trodes_py[3]
lfp_sampling_period = trodes_py[4]
start_time = 0

lfp_buffer = deque()
decision_list = [False, False, False]

lb.input_channel_id()
buffering_thread = threading.Thread(target=lb.lfp_buffering, args=(trodes_client, lfp_buffer, 500))
buffering_thread.start()

while True:
    if len(lfp_buffer) < 500:
        continue

    decision_list.append(rd.detection_with_rms(lfp_buffer, 8, 12, lfp_sampling_rate, 400))
    # this is problematic. the real lfp sampling rate is larger than 1250

    stimulation = True
    for m in range(len(decision_list)-3, len(decision_list)):
        if not decision_list[m]:
            stimulation = False

    print('Stimulation at timestamp ' + str(time.time_ns()) + ' is ' + str(stimulation))
    if stimulation:
        stim_msg = tc.call_statescript(trodes_hardware, 1)
        print("Stimulation status: "+str(stim_msg))