"""""""""
Written by Mengzhan Liufu and Sameera Shridhar at Yu Lab, the University of Chicago, December 2021
"""""""""

import TrodesReader
import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt


def bandpass_filter(filter_name, flattened_array, sampling_freq, order, lowcut, highcut):
    if filter_name == 'elliptical':
        sos = signal.ellip(order, 0.01, 120, [lowcut, highcut], btype='bp', output='sos', fs=sampling_freq)
    if filter_name == 'butterworth':
        sos = signal.butter(order, [lowcut, highcut], 'bp', fs=sampling_freq, output='sos')
    if filter_name == 'cheby1':
        sos = signal.cheby1(order, 1, [lowcut, highcut], 'bp', fs=sampling_freq, output='sos')
    if filter_name == 'cheby2':
        sos = signal.cheby2(order, 15, [lowcut, highcut], 'bp', fs=sampling_freq, output='sos')

    y = signal.sosfiltfilt(sos, flattened_array)

    return y


def calculate_rms(buffer):
    square_summed = 0
    for k in buffer:
        square_summed += (k ** 2)

    return math.sqrt(square_summed / len(buffer))


def filter_then_rms(buffer, low_cut, high_cut, threshold):
    filtered_buffer = bandpass_filter('butterworth', buffer, lfp_sampling_rate, 1, low_cut, high_cut)
    current_rms = calculate_rms(filtered_buffer)
    return current_rms >= threshold


## --------------------------- Input parameters --------------------------------------
lfp_sampling_rate = 1250
lfp_sampling_period = (1/lfp_sampling_rate)*(10**9)
data_path = r'C:\Users\mengz\Box\Jhan (Mengzhan Liufu)\ClosedLoopControl Project\DATA\20211117_testing_5min\20211117_testing_5min.LFP\20211117_testing_5min.LFP_nt28ch1.dat'

lower_bound = 10000
upper_bound = 19000
upper_freq = 250
lower_freq = 140
num_std = 3

## --------------------------- Data acquisition and filtering --------------------------------------

lfp_data = []
initial_data = []
data = TrodesReader.readTrodesExtractedDataFile(data_path)
all_data = data['data']

for i in range(0, 2499):
    current_data = all_data[i]
    initial_data.append(current_data[0])

for i in range(lower_bound, upper_bound):
    current_data = all_data[i]
    lfp_data.append(current_data[0])

filtered_data = bandpass_filter('butterworth', lfp_data, lfp_sampling_rate, 1, lower_freq, upper_freq)
## --------------------------- Offline detection --------------------------------------

offline_decision_list = [False, False]
offline_rms = []
offline_stimulation_list = []

for i in range(499, len(lfp_data)):
    current_buffer = filtered_data[i-499:i]
    offline_rms.append(calculate_rms(current_buffer))

avg_rms_offline = np.mean(offline_rms)
std_rms_offline = np.std(offline_rms)
threshold_rms_offline = avg_rms_offline + num_std*std_rms_offline

offline_zscored = []
for i in offline_rms:
    offline_zscored.append((i - avg_rms_offline) / std_rms_offline)
    offline_decision_list.append(i >= threshold_rms_offline)

    current_stimulation = True
    for m in range(len(offline_decision_list)-3,len(offline_decision_list)):
        if not offline_decision_list[m]:
            current_stimulation = False

    offline_stimulation_list.append(current_stimulation)

offline_decision_list.pop(0)
offline_decision_list.pop(0)
## --------------------------- Online detection --------------------------------------
online_decision_list = [False, False]
online_rms = []
online_stimulation_list = []

avg_initial = np.mean(initial_data)
std_initial = np.std(initial_data)
threshold_rms_online = avg_initial + num_std*std_initial

for i in range(499, len(lfp_data)):
    online_buffer = lfp_data[i-499:i]
    online_rms.append(calculate_rms(online_buffer))
    current_decision = filter_then_rms(online_buffer, lower_freq, upper_freq, threshold_rms_online)
    online_decision_list.append(current_decision)

    current_stimulation = True
    for m in range(len(online_decision_list)-3, len(online_decision_list)):
        if not online_decision_list[m]:
            current_stimulation = False

    online_stimulation_list.append(current_stimulation)

online_decision_list.pop(0)
online_decision_list.pop(0)

avg_online = np.mean(online_rms)
std_online = np.std(online_rms)

online_zscored = []
for i in online_rms:
    online_zscored.append((i-avg_online)/std_online)

## --------------------------- Accuracy and precision --------------------------------------
'''
TP = 0
FP = 0
TN = 0
FN = 0

for i in range(0,len(offline_stimulation_list)):
    if offline_stimulation_list[i] == True and online_stimulation_list[i] == True:
        TP += 1
    if offline_stimulation_list[i] == False and online_stimulation_list[i] == False:
        TN += 1
    if offline_stimulation_list[i] == False and online_stimulation_list[i] == True:
        FP += 1
    if offline_stimulation_list[i] == True and online_stimulation_list[i] == False:
        FN += 1

Accuracy = ((TP+TN)/(TP+TN+FP+FN))*100
Precision = TP/(TP+FP)
Recall = TP/(TP+FN)
'''
## --------------------------- Plotting --------------------------------------

fig1 = plt.figure(figsize=(40, 30))
plt.style.use("seaborn-white")
plt.yticks([])
grid1 = plt.GridSpec(13, 1, wspace=0, hspace=0)
ax1 = plt.subplot(grid1[0:3, 0:1])
ax2 = plt.subplot(grid1[3:6, 0:1])
ax3 = plt.subplot(grid1[6:9, 0:1])
ax4 = plt.subplot(grid1[9:12, 0:1])
ax5 = plt.subplot(grid1[12, 0:1])

ax1.plot(lfp_data[499:len(lfp_data)], color='k', alpha=0.5, label='Raw LFP')
#ax1.set_xlabel("Sample Count", fontsize=30)
ax1.set_ylabel("Power(µV)", fontsize=30)
#x1.set_title("Raw LFP Data", fontsize=40)
ax1.axhline(y=0, color='k', linewidth='2')
ax1.legend(fontsize=30)
#plt.yticks(np.arange(0.2, 1, step=0.2), fontsize=20)

ax2.plot(filtered_data[499:len(filtered_data)], color='b', alpha=0.5, label='Filtered LFP')
ax2.set_xlabel("Sample Count", fontsize=30)
ax2.set_ylabel("Power(µV)", fontsize=30)
#ax2.set_title("Filtered LFP Data", fontsize=40)
ax2.axhline(y=0, color='k', linewidth='2')
ax2.legend(fontsize=30)

ax3.plot(offline_zscored, color='g', linewidth='4', alpha=0.5, label='Offline Z-scored RMS')
ax3.axhline(y=num_std, color='r', linewidth='4', label='Offline Threshold')
ax3.set_ylim(bottom=-4, top=4)
#ax3.set_xlabel("Sample Count", fontsize=30)
ax3.set_ylabel("Z Score", fontsize=30)
ax3.axhline(y=0, color='k', linewidth='2')
#ax3.set_title("Z-scored RMS (offline)", fontsize=40)
ax3.legend(fontsize=30)

ax4.plot(online_zscored, color='b', linewidth='4', alpha=0.5, label='Online Z-scored RMS')
ax4.axhline(y=(threshold_rms_online-avg_online)/std_online, color='r', linewidth='4', label='Online Threshold')
ax4.set_ylim(bottom=-4, top=4)
#ax4.set_xlabel("Sample Count", fontsize=30)
ax4.axhline(y=0, color='k', linewidth='2')
ax4.set_ylabel("Z Score", fontsize=30)
#ax4.set_title("Z-scored RMS (online)", fontsize=40)
ax4.legend(fontsize=30)

for s in range(0, len(online_stimulation_list)):
    if online_stimulation_list[s]:
        ax5.axvline(x=s, color='k')

#ax5.set_xlabel("Sample Count", fontsize=30)
ax5.set_ylabel("True/False", fontsize=30)
#ax5.set_title("Stimulation Status", fontsize=40)
ax5.legend(['Stimulation Status'], fontsize=30)
ax5.set_xlabel('Sample Count', fontsize=50)

ax5_xticks = []
for i in range(1, 10):
    ax5_xticks.append(str(lower_bound+int(0.1*i*(upper_bound-lower_bound))))

plt.xticks(np.arange(0.1, 1, step=0.1), ax5_xticks, fontsize=30)
plt.show()

'''
fig2 = plt.figure()
plt.bar([0, 1, 2], [Accuracy, Precision, Recall], width=0.8, bottom=None, align='center', data = None)
plt.show()
'''