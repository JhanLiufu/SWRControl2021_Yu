'''
Written by Mengzhan Liufu at Yu Lab, University of Chicago
'''
import trodes_connection as tc
from data_buffering import data_buffering
# from determine_threshold import determine_threshold
from detector import Detector
from scipy.signal import butter
import threading

# ------------------------- Connect to trodes -------------------------
trodes_client, trodes_hardware, sampling_rate = tc.connect_to_trodes("tcp://127.0.0.1:49152", 20, 'lfp')

# ------------------------- Parameters -------------------------
myDetc = Detector(3, 150, 150, 250, 500, 600, 3, 6, 3, stim_threshold=10**35, noise_threshold=1000,
                  sampling_rate=sampling_rate)

# ------------------------- Initialize data buffer -------------------------
for i in range(myDetc.buffer_size):
    current_data = trodes_client.receive()['lfpData']
    myDetc.data_buffer.append(current_data[myDetc.target_channel])

# ------------------------- Start automatic data buffering -------------------------
buffering_thread = threading.Thread(target=data_buffering, args=(trodes_client, myDetc))
buffering_thread.start()

# ------------------------- Initialize filter -------------------------
butter_filter = butter(1, [myDetc.freq_lowcut, myDetc.freq_highcut], 'bp', fs=sampling_rate, output='sos')
myDetc.filter = butter_filter

# ------------------------- Start detecting -------------------------
while True:

    if myDetc.stim_status is not myDetc.decide_stim():
        tc.call_statescript(trodes_hardware, myDetc.stim_status+3)
        myDetc.flip_stim_status()
