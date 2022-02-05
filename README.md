# emkanalysis_clc_toolkit API reference

**bandpass_filter**(filter_name, flattened_array, sampling_freq, order, lowcut, highcut):

    Filter a signal array with bandpass

    @param filter_name: the type of filter to use
    @param flattened_array: 1D signal array to be filtered
    @param sampling_freq: the sampling frequency with which the signal is collected
    @param order:
    @param lowcut: lower bound of the frequency band of interest
    @param highcut: higher bound of the frequency band of interest
    
    @return y: the signal in frequency band [lowcut, highcut]

**convert_time**(time_file):

    Convert trodes timestamps into seconds

    @param time_file: trodes timestamps.dat source file
    
    @return np.array(time_data): numpy array of timestamps in seconds 
    
**hilbert_processing**(power_data):

    Apply Hilbert transformation to a power data series to get is magnitude envelope

    @param power_data: raw power data array
    
    @return hilbert_magnitude: magnitude envelope of power_data after hilbert transformation

**denoise**(power_data, time_data, noise_label, threshold):

    Remove data samples that are labeled as global noise from power series 

    @param power_data: data sample array
    @param time_data: timestamp array in seconds, match power_data in length
    @param noise_label: T/F array of each sample labeled as noise or not, match power_data in length
    @param threshold: a maximum value of power to be considered normal activity (instead of noise)
    
    @return denoised: array of samples without noise samples
    @retun denoised_time: timestamp array in seconds, match denoised in length

**detect**(magnitude, num_std, num_wait):

    Detect threshold crossing events in a given power series

    @param magnitude: power array for threshold-crossing events detection
    @param num_std: number of standard deviation above average (of power array) for threshold to be
    @param num_wait: the number of samples to wait before stimulating. i.e num_wait consecutive Trues then stimulate
    
    @return stimulation: numpy array of stimulation status (T/F) at each sample point in power array

**calculate_rms**(buffer):

    return the root mean-squared of a given array

    @param buffer: any array or list of number

    @return: the root mean-squared value of the array as a proxy for its power

**online_rms_processing**(power_data, sampling_rate, time_data, buffer_length, lower_bound, upper_bound, threshold):

    Process a given power array with stepwise (i.e online) RMS estimation

    @param power_data: array of raw power across time
    @param sampling_rate: 
    @param time_data: array of power_data's timestamps in seconds
    @param buffer_length: number of data samples for RMS estimation
    @param lower_bound: lower bound of target frequency range 
    @param upper_bound: upper bound of target frequency range
    @param threshold: maximum RMS value to be considered
    
    @return rms_magnitude: array of RMS-processed power series
    @return rms_time: array of rms_magnitude's timestamps in seconds

**offline_rms_processing**(power_data, time_data, buffer_length, threshold):

    Filter the whole given power array, then perform RMS estimation on buffer at each sample 

    @param power_data: array of raw power across time
    @param time_data: array of power_data's timestamps in seconds
    @param buffer_length: number of data samples for RMS estimation
    @param threshold: maximum RMS value to be considered
    
    @return rms_magnitude: array of RMS-processed power series
    @return rms_time: array of rms_magnitude's timestamps in seconds

**extract_events**(stimulation, timestamps):

    Extract timestamps of event onset, offset and duration array from stimulation status array

    @param stimulation: array of stimulation status (T/F) at each timestamp
    @param timestamps: array of timestamps in seconds that match the stimulation array
    
    @return np.array(changedtime): numpy array of timestamps of event onset and offset (alternative) in seconds
    @return np.array(eventduration): numpy array of event durations in milliseconds
    @return np.array(truetime): numpy array of timestamps in seconds of event onset only 

**deblip_with_duration**(truetime,eventduration,threshold):

    Remove the onset timestamps that belong to noise events based on event duration

    @param truetime: array of timestamps of event onset
    @param eventduration: array of event duration in milliseconds, should match array truetime in length
    @param threshold: minimum event duration to be considered a real event
    
    @return np.array(deblipped): array of timestamps in seconds without "blips"

**deblip_with_frequency**(truetime,threshold):

    Remove the onset timestamps that belong to noise events based on event frequency

    @param truetime: array of timestamps of event onset
    @param threshold: minimum time gap between two events for the second one to be considered a real event
    
    @return np.array(deblipped): array of timestamps in seconds without "blips"

**accuracy_precision_calculation**(detection_series_1, detection_series_2, window_width):

    detection_series_2 is used as ground truth reference to calculate the accuracy and precision of detection_series_1. 
    For a particular event in detection_series_2, if there exists an event in detection_series_1 that matches the one
    in series_2, we mark the one in series_2 (ground truth) as detected and the one in series_1 as truepositive (TP). 
    If an event in series_1 doesn't match any series_2 event, it's marked as falsepositive(FP).
    
    @param detection_series_1: timestamp (of the starts of events) arrays in seconds 
    @param detection_series_2: timestamp (of the starts of events) arrays in seconds
    @param window_width: range of detection time difference allowed in seconds
    
    @return accuracy: percentage of series_2 events detected in series_1
    @return precision: percentage of correct detections (TP) in series_1
    @return (len(detection_series_2)-len(truepositive)): number of series_2 events unmatched by any series_1 event

**lag_distribution**(time_series_1,time_series_2):

    Calculate general time lag distribution between two time series with cross correlation

    @param time_series_1: array of timestamps in seconds
    @param time_series_2: array of timestamps in seconds
    
    @return lag_distribution: array of cross-correlated time lags in milliseconds
