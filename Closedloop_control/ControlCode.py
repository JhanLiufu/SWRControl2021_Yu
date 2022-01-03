import trodes_connection as tc
import rms_detection as rd
import lfp_buffering as lb
import SyncTimestamp as st
from collections import deque
import threading
import time
import numpy as np

trodes_py = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20)
trodes_client = trodes_py[0]
trodes_hardware = trodes_py[1]
trodes_info = trodes_py[2]
lfp_sampling_rate = trodes_py[3]
lfp_sampling_period = trodes_py[4]

time_params = st.timestamp_sync(trodes_client, 2000)

# these parameters need to be saved for timestamp conversion and alignment in analysis
trodes_PC_dif = time_params[0]
system_dif = time_params[1]

lfp_buffer = deque()
buffering_thread = threading.Thread(target=lb.lfp_buffering, args=(trodes_client, lfp_buffer, 500))
buffering_thread.start()

stimulation_status = False
decision_list = [False, False, False]

with open('/media/nvme0/Data/clc/data/stim_03_unix.txt', 'a') as py_data:
    py_data.write(str(trodes_PC_dif)+"\n")
    # the first line tells the unix time difference between time_ns() and trodes
    py_data.write(str(system_dif)+"\n")
    # the second line tells how many nanoseconds do 20 sample counts correspond to
    while True:

        if len(lfp_buffer) < 500:
            continue

        decision_list.append(rd.detection_with_rms(lfp_buffer, 140, 250, lfp_sampling_rate, 200))
        stimulation = True
        for m in range(len(decision_list)-3, len(decision_list)):
            if not decision_list[m]:
                stimulation = False

        if (stimulation_status is False) and (stimulation is True):
            py_data.write(str(time.time_ns())+"\n")
            stim_msg = tc.call_statescript(trodes_hardware, 1)
            stimulation_status = True

        if (stimulation_status is True) and (stimulation is False):
            tc.call_statescript(trodes_hardware, 2)
            stimulation_status = False