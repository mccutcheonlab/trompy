# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 11:51:29 2020

@author: James Edgar McCutcheon
"""

import numpy as np
import scipy.signal as sig
from math import ceil

def processdata(data, datauv, method='konanur', normalize=True, normalize_time_cutoff=5, normalize_method="zscore", fs=1017):
    """ Corrects for baseline when given calcium-moldulated and non-Ca modulated streams.

    Parameters
    ----------
    data : List or 1D array of Floats
        Primary data stream (Ca-modulated).
    datauv : List or 1D array of Floats
        Secondary data stream (non-Ca modulated).
    method : Str, optional
        Chooses method to correct. Options are 'konanur', 'lerner-davidson', 'lerner') The default is 'konanur'.
        'konanur' was developed by Vaibhav Konanur and uses FFT as described in
        doi: 10.1016/j.physbeh.2019.112771
        
        'lerner-davidson' (aka lerner or davidson) uses regression and was developed
        by Tom Davidson and used by Talia Lerner as described in
        doi: 10.1016/j.cell.2015.07.014
        
        Code adapted from https://github.com/tjd2002/tjd-shared-code/tree/master/matlab/photometry/FP_normalize.m
        
    normalize : Bool, optional
        Normalizes signal by method given in normalize_method. The default is True.
    normalize_time_cutoff : Int, optional
        Time in minutes at beginning and end to ignore when normalizing signal.
        If too long (> a quarter of total time) then it is reduced. The default is 5 (min).
    normalize_method : Str, optional
        Default is zscore. Other options are 'df' for deltaF/F and "old" which scales based on an arbitrary 3*SD.
    fs : Int, optional
        Used when normalizing signal. 1017 is default.

    Returns
    -------
    df : List or 1D array of Floats
        Processed signal, corrected for isosbestic.

    """
    if method == 'konanur':
        pt = len(data)
        X = np.fft.rfft(datauv, pt)
        Y = np.fft.rfft(data, pt)
        Ynet = Y-X
    
        df = np.fft.irfft(Ynet) 
        df = sig.detrend(df)
    
        b, a = sig.butter(9, 0.012, 'low', analog=True)
        df = sig.filtfilt(b, a, df)
        
    elif method == 'lerner' or method == 'lerner-davidson' or method == 'davidson':
        x = np.array(datauv)
        y = np.array(data)
        bls = np.polyfit(x, y, 1)
        Y_fit_all = np.multiply(bls[0], x) + bls[1]
        Y_dF_all = y - Y_fit_all
        df = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
        
    else:
        print(method, 'is not a valid method.')
        
    if normalize==True:
        fs = int(fs)
        total_length = len(df) / (60*fs)

        if total_length < normalize_time_cutoff*2:
            nsamples = int((total_length / 4) * 60 * fs)
            print("File is too short ({:.1f} minutes) for {} minute cutoff. Using {:.1f} minutes instead.".format(
                total_length, normalize_time_cutoff, nsamples / (60*fs)))
        else:
            nsamples = normalize_time_cutoff*60*fs
            
        cutoff_range = range(nsamples, len(df)-nsamples)
        mean=np.mean(df[cutoff_range])
        sd=np.std(df[cutoff_range])
        
        if normalize_method == "zscore":
            df_corr = np.subtract(df, mean)
            df=np.divide(df_corr, sd)
        elif normalize_method == "df":
            df=np.divide(df, np.abs(mean))*100
        elif normalize_method == "old":
            df=np.divide(df, sd*3)
    
    return df

def snipper(data, timestamps, fs=1, baseline_length=10, trial_length=30,
                 adjust_baseline = True,
                 bins = 0, **kwargs):
    """ Makes 'snips' of a data file aligned to an event of interest.

    Parameters
    ----------
    data : List or array of floats
        Data to be divided into snips.
    timestamps : List
        Timestamps of events to be used to align data.
    fs : Float, optional
        Sampling frequency. The default is 1.
    baseline_length : Int or List of two Ints, optional
        Number of seconds to include before event, if single value.
        For baseline between -x and -y, provide a list of [x, y].
        The default is 10.
    trial_length : Int, optional
        Total length (in seconds) of each snip. The default is 30.
    adjust_baseline : Bool, optional
        When True divides all data points in each snip by mean of points occurring before event. The default is True.
    bins : Int, optional
        Number of bins to divide trial length into. The default is 0. If set at default
        of 0 then no binning will occur.

    Returns
    -------
    snips : List of lists
        List of X snips of Y length where X=number of events in timelock and Y=bins
    pps : Int
        Samples (points) per second 

    """
    # legacy arguments
    if "timelock " in kwargs.keys():
        timestamps = kwargs["timelock"]
    
    if "preTrial" in kwargs.keys():
        baseline_length = kwargs["preTrial"]

    if "trialLength" in kwargs.keys():
        trial_length = kwargs["trialLength"]
    
    if "adjustBaseline" in kwargs.keys():
        adjust_baseline = kwargs["adjustBaseline"]

    if 't2sMap' in kwargs.keys():
        print("Use of t2sMap is no longer supported. Use fs instead or install trompy=<14.0")
        return
    
    if len(timestamps) == 0:
        print('No events to analyse! Quitting function.')
        raise Exception('no events')
    
    # removes non-numeric values, e.g. nans or infinite
    timestamps = [i for i in timestamps if np.isfinite(i)]
    
    events_in_samples = [ceil(timestamp*fs) for timestamp in timestamps]
    
    try:
        if len(baseline_length) == 2:
            baseline_start_in_samples = int(baseline_length[0]*fs)
            baseline_end_in_samples = int((baseline_length[0]-baseline_length[1])*fs)
        else:
            print("Incorrect number of values given for baseline_length. Using first value only.")
            baseline_start_in_samples = int(baseline_length[0]*fs)
            baseline_end_in_samples = int(baseline_length[0]*fs)
    except TypeError:
        baseline_start_in_samples = int(baseline_length*fs)
        baseline_end_in_samples = int(baseline_length*fs)

    trial_length_in_samples = int(trial_length*fs)

    # removes events where an entire snip cannot be made
    events_in_samples = [event for event in events_in_samples if \
        (event-baseline_start_in_samples > 0) and \
        (event-baseline_start_in_samples+trial_length_in_samples) < len(data)]

    n_snips = len(events_in_samples)
    snips = np.empty([n_snips, trial_length_in_samples])
    
    trial_start = [event - baseline_start_in_samples for event in events_in_samples]
    trial_end = [start + trial_length_in_samples for start in trial_start]

    for idx, (start, end) in enumerate(zip(trial_start, trial_end)):
        snips[idx] = data[start : end]

    if adjust_baseline == True:
        average_baseline = np.mean(snips[:,:baseline_end_in_samples], axis=1)
        snips = np.subtract(snips.transpose(), average_baseline).transpose()
        # snips = np.divide(snips.transpose(), np.abs(average_baseline)).transpose()

    if bins > 0:
        if trial_length_in_samples % bins != 0:
            snips = snips[:,:-(trial_length_in_samples % bins)]
        totaltime = snips.shape[1] / int(fs)
        snips = np.mean(snips.reshape(n_snips,bins,-1), axis=2)
        pps = bins/totaltime
              
    return snips, int(fs)

def mastersnipper(data, dataUV, data_filt, fs, events,
                  trialLength=30,
                  snipfs=10,
                  preTrial=10,
                  threshold=8,
                  peak_between_time=[0, 1],
                  latency_events=[],
                  latency_direction='pre',
                  max_latency=30,
                  verbose=True,
                  removenoisefromaverage=True,
                  **kwargs):

    """ Runs snipper function on several types of data streams and calculates noise trials.

    Parameters
    ----------
    data : List or 1D array
        Primary data stream (normally from blue channel).
    dataUV : List or 1D array
        Secondary data stream (normally from UV channel).
    data_filt : List or 1D array
        Filtered data stream (normally after Lerner or Vaibhav correction of data and dataUV).
    t2sMap : List
        Time-to-sample map.
    fs : Float
        Sample frequency.
    events : List of floats
        Timestamps of events for data to be aligned to.
    bins : Int, optional
        Number of bins for snips to be in length. The default is 300.
    baselinebins : Int, optional
        Number of bins for baseline. The default is 100.
    preTrial : Int, optional
        Time (in seconds) before event. The default is 10.
    trialLength : Int, optional
        Time (in seconds) for entire snip/trial. The default is 30.
    threshold : Int or Float, optional
        Noise threshold factor - snips that exceed threshold x bgMAD are considered 'noisy'. The default is 8.
    peak_between_time : List, optional
        Start and stop times for peak calculation. The default is [0, 1].
    latency_events : List, optional
        Timestamps for latency events. The default is [].
    latency_direction : String, optional
        Either 'pre' or 'post' depedning on whether to search for first latency before or after alignment event. The default is 'pre'.
    max_latency : Int or Float, optional
        Amount of time before or after alignment event to search for a latency event. The default is 30.
    verbose : Bool, optional
        Prints out information as it analyzes. The default is True.

    Returns
    -------
    output, a dictionary with the following keys
    'blue' : 2D array (or list of lists of floats)
        Snips of primary data stream.
    'uv' : 2D array (or list of lists of floats)
        Snips of secondary data stream.
    'filt' : 2D array (or list of lists of floats)
        Snips of filtered data stream.    
    'filt_z' : 2D array (or list of lists of floats)
        Snips of Z-scored filtered data stream.         
    'filt_avg' : 1d array (or list of floats)
        Average (mean) of filtered snips.
    'filt_avg_z' : 1d array (or list of floats)
        Average (mean) of filtered snips converted to z-score.
    'noise' : List of Booleans    
        Logical index of noisy trials.
    'peak' : List of floats
        Peak values for all snips.
    'latency' : List of floats
        Latency times for all trials.

    """
    # Parse arguments relating to trial length, bins etc

    if preTrial > trialLength:
        baseline = trialLength / 2
        print("preTrial is too long relative to total trialLength. Changing to half of trialLength.")
    else:
        baseline = preTrial
    
    if 'bins' in kwargs.keys():
        bins = kwargs['bins']
        print(f"bins given as kwarg. Fs for snip will be {trialLength/bins} Hz.")
    else:
        if snipfs > fs-1:
            print('Snip fs is too high, reducing to data fs')
            bins = 0
        else:
            bins = int(trialLength * snipfs)
    
    print('Number of bins is:', bins)
    
    if 'baselinebins' in kwargs.keys():
        baselinebins = kwargs['baselinebins']
        if baselinebins > bins:
            print('Too many baseline bins for length of trial. Changing to length of baseline.')
            baselinebins = int(baseline*snipfs)
        baselinebins = baselinebins
    else:
        baselinebins = int(baseline*snipfs)
    
    if len(events) < 1:
        print('Cannot find any events. All outputs will be empty.')
        return {}
    else:
        if verbose: print('{} events to analyze.'.format(len(events)))

    if len(data) > 0:
        blueTrials,_ = snipper(data, events,
                                       fs=fs,
                                       bins=bins,
                                       preTrial=baseline,
                                       trialLength=trialLength)
    else:
        print('No data stream available as primary data input. Exiting without snipping.')
        return {}
    
    if len(dataUV) > 0:
        uvTrials,_ = snipper(dataUV, events,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=baseline,
                                   trialLength=trialLength)
    else:
        print('No UV (secondary) data stream.')
        uvTrials = []
    if len(data_filt) > 0:
        filtTrials,_ = snipper(data_filt, events,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=baseline,
                                   trialLength=trialLength,
                                   adjustBaseline=False)

        filtTrials_z = np.asarray(zscore(filtTrials, baseline_points=baselinebins))
    else:
        print('No processed data stream.')
        filtTrials, filtTrials_z  = [], []

    # Code to calculate noise in file and work out which trials should be classified as noisy
    if 'bgMAD' not in kwargs.keys():
        bgMAD = findnoise(data, makerandomevents(120, int(len(data)/fs)-120),
                              fs=fs, bins=bins,
                              method='sum')
    else:
        bgMAD = kwargs['bgMAD']

    sigSum = [np.sum(abs(i)) for i in blueTrials]
    noiseindex = [i > bgMAD*threshold for i in sigSum]

    if sum(noiseindex) == len(noiseindex):
        print('Not removing noisy trials from average because all trials identified as noisy.')
        removenoisefromaverage = False
    if len(filtTrials) > 0:
        if removenoisefromaverage:
                filt_avg = np.mean(removenoise(filtTrials, noiseindex), axis=0)
                if verbose: print('{} noise trials removed from averages'.format(sum(noiseindex)))
        else:
            filt_avg = np.mean(filtTrials, axis=0)
            
        filt_avg_z = [(x-np.mean(filt_avg))/np.std(filt_avg) for x in filt_avg]
    else:
        filt_avg, filt_avg_z  = [], []
    
    # Code to find peak at specified time in each trial
    bin2s = bins/trialLength
    peakbins = [int((preTrial+peak_between_time[0])*bin2s),
                int((preTrial+peak_between_time[1])*bin2s)]
    peak = [np.mean(trial[peakbins[0]:peakbins[1]]) for trial in filtTrials_z]
    
    # Code to find latencies associated with each trial
    latency = []
    if len(latency_events) > 1: 
        for event in events:
            if latency_direction == 'pre':
                try:
                    latency.append(np.abs([lat-event for lat in latency_events if lat-event<0]).min())
                except ValueError:
                    latency.append(np.NaN)
            
            elif latency_direction == 'post':
                try:
                    latency.append(np.abs([lat-event for lat in latency_events if lat-event>0]).min())
                except ValueError:
                    latency.append(np.NaN)

        latency = [x if (x<max_latency) else np.NaN for x in latency]
        if latency_direction == 'pre':
            latency = [-x for x in latency]
    else:
        print('No latency events found')
        
    # Create info dictionary
    info = {}
    info['baseline'] = baseline
    info['length'] = trialLength
    if bins == 0:
        info['bins'] = np.shape(blueTrials)[1]
    else:
        info['bins'] = bins
    info['snipfs'] = info['bins'] / info['length']

    output = {}
    output['blue'] = blueTrials
    output['uv'] = uvTrials
    output['filt'] = filtTrials
    output['filt_z'] = filtTrials_z
    output['filt_avg'] = filt_avg
    output['filt_avg_z'] = filt_avg_z
    output['noise'] = noiseindex
    output['peak'] = peak
    output['latency'] = latency
    output['info'] = info
    
    return output

def zscore(snips, baseline_points=100):
    """
    Converts list or array of snips into Z-scored values.

    Parameters
    ----------
    snips : List of lists or 2D Array
        Data to be converted into z-scores.
    baseline_points : Int, optional
        Number of bins or points to be used as the baseline for z-score calculation. The default is 100.

    Returns
    -------
    z_snips : List of lists
        Converted snips expressed as z-scores.
    """
    
    BL_range = range(baseline_points)
    z_snips = []
    for i in snips:
        mean = np.mean(i[BL_range])
        sd = np.std(i[BL_range])
        z_snips.append([(x-mean)/sd for x in i])
        
    return z_snips

def findnoise(data, background_events, fs = 1, bins=0, method='sd'):
    """
    Identifies snips that are classed as noisy due to exceeding a threshold based on background.

    Parameters
    ----------
    data : List or 1D array of Floats
        Data stream from entire session.
    background_events : List of floats
        Timestamps from which background snips will be made.
    t2sMap : List of floats, optional
        Time-to-samples map. The default is [].
    fs : Float, optional
        Sampling frequency. The default is 1.
    bins : Int, optional
        Number of bins to be used for snips. The default is 0.
    method : Str, optional
        Method of calculating noise. 'sd' or 'sum' (standard deviation or sum). Default is 'sd'.

    Returns
    -------
    bgMAD : Float
        Median absoluate deviation of background trials.

    """
    
    bgSnips, _ = snipper(data, background_events, fs=fs, bins=bins)
    
    if method == 'sum':
        bgSum = [np.sum(abs(i)) for i in bgSnips]
        bgMAD = med_abs_dev(bgSum)
    elif method == 'sd':
        bgSD = [np.std(i) for i in bgSnips]
        bgMAD = med_abs_dev(bgSD)
   
    return bgMAD

def removenoise(snipsIn, noiseindex):
    """
    Removes snips that have been classified as noisy.

    Parameters
    ----------
    snipsIn : List of lists or Numpy array
        Snips (generally list of binned data).
    noiseindex : List of Booleans
        Should be the same length as first dimension of snipsIn.

    Returns
    -------
    snipsOut : List of lists
        Snips with noisy snips removed.

    """
    snipsOut = np.array([x for (x,v) in zip(snipsIn, noiseindex) if not v])   
    return snipsOut

def med_abs_dev(data, b=1.4826):
    """
    Calcuates median absolute deviation. See doi:10.1016/j.jesp.2013.03.013

    Parameters
    ----------
    data : List or 1D array
        Data to be analyzed.
    b : Float, optional
        Constant for calcuation. The default is 1.4826.

    Returns
    -------
    mad : Float
        Median absolute deviation of data.

    """
    median = np.median(data)
    devs = [abs(i-median) for i in data]
    mad = np.median(devs)*b
                   
    return mad

def makerandomevents(minTime, maxTime, spacing = 77, n=100):
    """
    Generates pseudorandom event timestamps in between a start and stop time.
    Rather than using purely random selection should ensure events are tiled.

    Parameters
    ----------
    minTime : Int
        Minimum time (in seconds).
    maxTime : Int
        Maximum time (in seconds).
    spacing : Int, optional
        Time (in seconds) between consecutive events. Provides pseudorandom timing. The default is 77.
    n : Int, optional
        Number of timestamps to generate. The default is 100.

    Returns
    -------
    events : List
        Pseudorandonm timestamps.

    """
    events = []
    total = maxTime-minTime
    start = 0
    for i in np.arange(0,n):
        if start > total:
            start = start - total
        events.append(start)
        start = start + spacing
    events = [i+minTime for i in events]
    return events

def time2samples(data, fs):
    """
    Makes time2samples map (t2sMap) used to convert from timestamps to sample number.
    
    Edited 20-04-2020 - removed Tick as necessary argument.

    Parameters
    ----------
    data : List or 1D array
        Streamed photometry data.
    fs : Float
        Sample frequency.

    Returns
    -------
    t2sMap : 1D array
        Array of time (in second) for  number of samples in data.

    """
    t2sMap = np.linspace(1, len(data), len(data)) / fs
    
    # maxsamples = len(tick)*int(fs)
    # if (len(data) - maxsamples) > 2*int(fs):
    #     print('Something may be wrong with conversion from time to samples')
    #     print(str(len(data) - maxsamples) + ' samples left over. This is more than double fs.')
    #     t2sMap = np.linspace(min(tick), max(tick), maxsamples)
    # else:
    #     t2sMap = np.linspace(min(tick), max(tick), maxsamples)
        
    return t2sMap
    
def event2sample(EOI, t2sMap):
    """
    Returns sample number for an event.

    Parameters
    ----------
    EOI : Float
        Timestamp of an event (in seconds).
        
    t2sMap : 1D array
        Array of times to convert to sample number

    Returns
    -------
    idx : Int
        Index for event of interest in t2sMap, e.g. sample number.

    """
    idx = (np.abs(t2sMap - EOI)).argmin()   
    return idx

def resample_snips(snips, factor=0.1):
    """ Resamples snips to collapse data into larger bins (e.g. for ROC analysis)
    
    Parameters
    ------------
    snips : 2D array or list of lists of floats
        Snips to be resampled.
    factor : Float, optional
        Constant to determine how to bin data. Default is 0.1.
    
    Returns
    snips : 2D array or list of lists of floats
        Resampled snips.
    
    """
    if len(snips)>0:
        n_bins = len(snips[0])
        out_bins = int(n_bins * factor)

        snips_out = []
        for snip in snips:
            snips_out.append(np.mean(np.reshape(snip, (out_bins, -1)), axis=1))
    
        return snips_out
    else:
        return []