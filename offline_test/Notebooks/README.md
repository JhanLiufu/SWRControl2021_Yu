# OfflineAnalysis_Finale Documentation

This notebook mainly serves to calculate the accuracy and precision of our online detection algorithm, using either hilbert transformed
data or RMS-estimated data as ground truth. Relevant plots are also generated for the sake of checking.

---

## Variable Naming Pattern

All variables (including lists, arrays and constants) in this notebook follow this naming pattern: ```[detection type]_[processing method]_[description]```.
Using this fixed pattern and the notebook layout, all variable names should be predictable and easily trackable.

1. **Detection type**: **online**,**offline** or **noise**. **offline** means filtering the whole recording in ripple range first, and 
**online** means creating buffers of a certain length at each sample point then filtering the buffers (our online detection algorithm).
**noise** means filtering the raw data in noise range (500~600 Hz) in order to identify global noise events. 
2. **processing method**: **hilbert** or **rms**. Offline ripple data is either processed with hilbert transformation or RMS estimation
and then used as ground truth for calculations of accuracy and precision. Online detection uses RMS in real time.
3. **description**: all data bands using either hilbert method or RMS method have many common modalities (i.e variables) like **_magnitude**,
**_deblipped**, **_timetrue**, **_eventduration** etc. Here's a complete list of these arrays:

- ```_analytic```: this is the analytic signal array returned by Hilbert transformation
- ```_magnitude```: the raw data envelope of offline hilbert, offline RMS and online RMS
- ```_avg```: the average value of _magnitude
- ```_std```: the standard deviation of array _magnitude
- ```_threshold```: the power threshold determined with _avg and _std for detection. Except for noise_hilbert_threshold, which has a fixed
 value
- ```_zscore```: the z-scored version of _magnitude
- ```_decision```: arrays of True and False. Each element indicates whether its corresponding sample point crosses threshold or not
- ```_decarr```: _decision lists transformed to np.array. Contain exactly the same elements as _decision
- ```_stimulation```: arrats of True and False. Each element indicates stimulation status at each sample point (wait for three consecutive
 True decision to stimulation)
- ```_stimarr```: _stimulation lists transformed to np.array
- ```_denoised```: discarded elements in the **offline_hilbert_magnitude** list that are labelled as noise samples
- ```_time```: arrays of timestamps, corresponding to offline_hilbert_denoised, offline_rms_magnitude and online_rms_magnitude
- ```_raw```: an extra suffix besides the three. offline_hilbert_ variables with this tag are calculated without denoising
- ```_changedtime```: array of timestamps where stimulation status changes (event onset and offset)
- ```_truetime```: array of only the event onset timestamps from _changedtime
- ```_eventduration```: array of event durations, calculated with pairs of onset timestamp and offset timestamp from _changedtime
- ```_deblipped```: for offline_hilbert and online_rms, there are short-lived "blips" that come before real stimulation activities. 
Timestamps in the _truetime list that correspond to events lasting less than _lenthreshold milliseconds are discarded
- ```_lenthreshold```: the minimum event duration that we consider a real stimulation activity
- ```diffbar```, ```bin_edges```: used to create histogram
- ```_truepositive```: the timestamps of events which correctly respond to a ground truth event
- ```_falsepositive```: the timestamps of events that do not math any ground truth event
- ```_accuracy```, ```_precision```: as the names suggest

--- 

## Notebook Section Guide

The section guide here helps locate things in the notebook. 

- **1 Import packages and load methods**
- **2 Load Data and Initial Processing**
- &nbsp;&nbsp;&nbsp;2.1 Load Data
- &nbsp;&nbsp;&nbsp;2.2 Convert time frame
- &nbsp;&nbsp;&nbsp;2.3 Filtering
- **3 Offline&Noise Processing with Hilbert**
- &nbsp;&nbsp;&nbsp;3.1 Hilbert Transform
- &nbsp;&nbsp;&nbsp;3.2 Noise Event Detection
- &nbsp;&nbsp;&nbsp;3.3 Offline(Hilbert) Denoising
- &nbsp;&nbsp;&nbsp;3.4 Offline(Hilbert) Detection
- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.4.1 Detect with Denoised Offline(Hilbert) Data
- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.4.2 Detect with Denoised Offline(Hilbert) Data (no denoising)
- &nbsp;&nbsp;&nbsp;3.5 Offline(Hilbert) Deblipping
- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.5.1 Deblipping denoised Offline(Hilbert) data
- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.5.1 Deblipping denoised Offline(Hilbert) data (no denoising)
- **4 Offline Processing with RMS**
- &nbsp;&nbsp;&nbsp;4.1 Offline RMS (all ripple data)
- &nbsp;&nbsp;&nbsp;4.2 Offline(RMS) Detection
- &nbsp;&nbsp;&nbsp;4.3 Offline(RMS) Deblipping
- **5 Online RMS Processing**
- &nbsp;&nbsp;&nbsp;5.1 Online RMS (buffers)
- &nbsp;&nbsp;&nbsp;5.2 Online RMS Detection
- &nbsp;&nbsp;&nbsp;5.3 Online RMS Deblipping
- **6 Accuracy and Precision**
- &nbsp;&nbsp;&nbsp;6.1 Online(RMS) vs. Offline(Hilbert)
- &nbsp;&nbsp;&nbsp;6.2 Online(RMS) vs. Offline(RMS)