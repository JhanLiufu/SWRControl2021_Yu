import TrodesReader
from collections import deque
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
    # current_rms = calculate_rms(buffer)
    if current_rms >= threshold:
        return True, current_rms
    else:
        return False, current_rms


def detection_with_rms_no_filter(buffer, low_cut, high_cut, threshold):
    # filtered_buffer = bandpass_filter('butterworth', buffer, lfp_sampling_rate, 1, low_cut, high_cut)
    # current_rms = calculate_rms(filtered_buffer)
    current_rms = calculate_rms(buffer)
    if current_rms >= threshold:
        return True, current_rms
    else:
        return False, current_rms

## --------------------------- Input parameters --------------------------------------

lfp_sampling_rate = input("Enter LFP Sampling Rate:")
lfp_sampling_period = (1/lfp_sampling_rate)*(10**9)

data_path = input("Enter full data path:")
#timestamp_path = input("Enter timestamp path")
savefig_path = input("Enter the full path of your folder to save figures:")

upper_bound = input("Enter the upper bound of data (include a 500-sample buffer ahead of"
                    "the intended start, upper bound no smaller than 3000):")
lower_bound = input("Lower bound:")

upper_freq = input("Enter the highcut of your target frequency:")
lower_freq = input("Enter the lowcut of your target frequency:")
num_std = input("Enter the number of std above mean for thresholding:")

## --------------------------- Data acquisition and filtering --------------------------------------

lfp_data = []
initial_data = []
data = TrodesReader.readTrodesExtractedDataFile(data_path)
#timestamps = TrodesReader.readTrodesExtractedDataFile(timestamp_path)
all_data = data['data']

for i in range(0,2499):
    current_data = all_data[i]
    initial_data.append(current_data[0])

for i in range(upper_bound, lower_bound):
    current_data = all_data[i]
    lfp_data.append(current_data[0])

filtered_data = bandpass_filter('butterworth', lfp_data, lfp_sampling_rate, 1, lower_freq, upper_freq)

## --------------------------- Offline detection --------------------------------------

offline_decision_list = [False, False]
offline_rms = []
offline_stimulation_list = []
for i in range(upper_bound+499, lower_bound):
    current_buffer = filtered_data[i-499:i]
    offline_rms.append(calculate_rms(current_buffer))

    current_stimulation = True
    for m in range(len(offline_decision_list)-3, len(offline_decision_list)):
        if not offline_decision_list[m]:
            current_stimulation = False

    offline_stimulation_list.append(current_stimulation)


avg_rms_offline = np.mean(offline_rms)
std_rms_offline = np.std(offline_rms)

offline_zscored = []
for i in offline_rms:
    offline_zscored.append((i-avg_rms_offline)/std_rms_offline)

threshold_rms_offline = avg_rms_offline + num_std*std_rms_offline

## --------------------------- Online detection --------------------------------------

online_decision_list = [False, False]
online_rms = []
online_stimulation_list = []

avg_initial = np.mean(initial_data)
std_initial = np.std(initial_data)
threshold_rms_online = avg_initial + num_std*std_initial

for i in range(upper_bound+499, lower_bound):
    online_buffer = lfp_data[i-499:i]
    current_decision = filter_then_rms(online_buffer, lower_freq, upper_freq, threshold_rms_online)
    online_decision_list.append(current_decision[0])
    online_rms.append(current_decision[1])

    current_stimulation = True;
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

## --------------------------- Plotting --------------------------------------

fig1 = plt.figure(figsize=(40,40))
grid1 = plt.GridSpec(13, 1,wspace=0.5, hspace=0)
ax1 = plt.subplot(grid1[0:3, 0:1])
ax2 = plt.subplot(grid1[4:6, 0:1])
ax3 = plt.subplot(grid1[7:9, 0:1])
ax4 = plt.subplot(grid1[10:12, 0:1])
ax5 = plt.subplot(grid1[13, 0:1])

ax1.plot(lfp_data[upper_bound+499:lower_bound], color='k', alpha=0.5)
ax2.plot(filtered_data[upper_bound+499:lower_bound], color='b', alpha=0.5)
ax3.plot(offline_zscored, color='g', alpha=0.5)
ax3.axhline(y=num_std, color='k', linewidth='4')
ax4.plot(online_zscored, color='r', alpha=0.5)
ax4.axhline(y=num_std, color='k', linewidth='4')

for s in range(0,len(online_stimulation_list)):
    if online_stimulation_list[s]:
        ax5.axvline(x=s, color='k')

plt.grid(True)
plt.show()

fig2 = plt.figure()
plt.bar([0, 1, 2], [Accuracy, Precision, Recall], width=0.8, bottom=None, align='center', data=None)
plt.show()