# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 11:51:29 2020

@author: admin
"""

import numpy as np

def snipper(data, timelock, fs = 1, t2sMap = [], preTrial=10, trialLength=30,
                 adjustBaseline = True,
                 bins = 0):
    """
    Makes 'snips' of a data file aligned to an event of interest.

    If a timelocked map is needed to align data precisely (e.g. with TDT equipment)
    then it is necessary to pass a t2sMap to the function.

    Parameters
    ----------
    data : List or array of floats
        Data to be divided into snips.
    timelock : List
        Timestamps of events to be used to align data.
    fs : Float, optional
        Sampling frequency. The default is 1.
    t2sMap : List, optional
        Map to convert time (in seconds) to sample numbers. The default is [].
    preTrial : Int, optional
        Number of seconds to include before event. The default is 10.
    trialLength : Int, optional
        Total length (in seconds) of each snip. The default is 30.
    adjustBaseline : Bool, optional
        When True divides all data points in each snip by mean of points occurring before event. The default is True.
    bins : Int, optional
        Number of bins to divide trial length into. The default is 0.

    Returns
    -------
    snips : List of lists
        List of X snips of Y length where X=number of events in timelock and Y=bins
    pps : Float
        Points-per-second

    """

    if len(timelock) == 0:
        print('No events to analyse! Quitting function.')
        raise Exception('no events')

    pps = int(fs) # points per sample
    pre = int(preTrial*pps) 
#    preABS = preTrial
    length = int(trialLength*pps)
# converts events into sample numbers
    event=[]
    if len(t2sMap) > 1:
        for x in timelock:
            event.append(np.searchsorted(t2sMap, x, side="left"))
    else:
        event = [x*fs for x in timelock]

    new_events = []
    for x in event:
        if int(x-pre) > 0:
            new_events.append(x)
    event = new_events

    nSnips = len(event)
    snips = np.empty([nSnips,length])
    avgBaseline = []

    for i, x in enumerate(event):
        start = int(x) - pre
        avgBaseline.append(np.mean(data[start : start + pre]))
        try:
            snips[i] = data[start : start+length]
        except ValueError: # Deals with recording arrays that do not have a full final trial
            snips = snips[:-1]
            avgBaseline = avgBaseline[:-1]
            nSnips = nSnips-1

    if adjustBaseline == True:
        snips = np.subtract(snips.transpose(), avgBaseline).transpose()
        snips = np.divide(snips.transpose(), avgBaseline).transpose()

    if bins > 0:
        if length % bins != 0:
            snips = snips[:,:-(length % bins)]
        totaltime = snips.shape[1] / int(fs)
        snips = np.mean(snips.reshape(nSnips,bins,-1), axis=2)
        pps = bins/totaltime
              
    return snips, pps



def mastersnipper(data, dataUV, data_filt,
                  t2sMap, fs, bgMAD,
                  events,
                  bins=300,
                  baselinebins=100,
                  preTrial=10,
                  trialLength=30,    
                  threshold=8,
                  peak_between_time=[0, 1],
                  latency_events=[],
                  latency_direction='pre',
                  max_latency=30,
                  verbose=True):
    """
    Runs snipper function on several types of data streams and calculates noise trials.

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
    bgMAD : Float
        Median absolute debiation of background noise.
    events : List
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
    output : Dictionary
        Contains the following keys - 
            output['blue'] = snips of primary data stream
            output['uv'] = snips of secondary data stream
            output['filt'] = snips of filtered data stream
            output['filt_z'] = snips of Z-scores of filtered data stream
            output['filt_z_adjBL'] = snips of Z-scores of filtered data stream with adjusted baseline
            output['filt_avg'] = average of filtered snips
            output['filt_avg_z'] = average of filtered snips converted to Z-score
            output['noise'] = Boolean list of noisy trials
            output['peak'] = List of peak values for all snips
            output['latency'] = List of latency times for all trials

    """
    
    if len(events) < 1:
        print('Cannot find any events. All outputs will be empty.')
        blueTrials, uvTrials, filtTrials, filtTrials_z, filtTrials_z_adjBL, filt_avg, filt_avg_z, noiseindex, peak, latency = ([] for i in range(10))
    else:
        if verbose: print('{} events to analyze.'.format(len(events)))
        
        blueTrials,_ = snipper(data, events,
                                   t2sMap=t2sMap,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=preTrial,
                                   trialLength=trialLength)
        uvTrials,_ = snipper(dataUV, events,
                                   t2sMap=t2sMap,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=preTrial,
                                   trialLength=trialLength)
        filtTrials,_ = snipper(data_filt, events,
                                   t2sMap=t2sMap,
                                   fs=fs,
                                   bins=bins,
                                   preTrial=preTrial,
                                   trialLength=trialLength,
                                   adjustBaseline=False)
        
        filtTrials_z = zscore(filtTrials, baseline_points=baselinebins)
        filtTrials_z_adjBL = zscore(filtTrials, baseline_points=50)

        sigSum = [np.sum(abs(i)) for i in filtTrials]
        sigSD = [np.std(i) for i in filtTrials]

        noiseindex = [i > bgMAD*threshold for i in sigSum]
                        
        # do i need to remove noise trials first before averages
        filt_avg = np.mean(removenoise(filtTrials, noiseindex), axis=0)
        if verbose: print('{} noise trials removed'.format(sum(noiseindex)))
        filt_avg_z = zscore(filt_avg)

    
        bin2s = bins/trialLength
        peakbins = [int((preTrial+peak_between_time[0])*bin2s),
                    int((preTrial+peak_between_time[1])*bin2s)]
        peak = [np.mean(trial[peakbins[0]:peakbins[1]]) for trial in filtTrials_z]
        
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

    output = {}
    output['blue'] = blueTrials
    output['uv'] = uvTrials
    output['filt'] = filtTrials
    output['filt_z'] = filtTrials_z
    output['filt_z_adjBL'] = filtTrials_z_adjBL
    output['filt_avg'] = filt_avg
    output['filt_avg_z'] = filt_avg_z
    output['noise'] = noiseindex
    output['peak'] = peak
    output['latency'] = latency
    
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

def findnoise(data, background_events, t2sMap = [], fs = 1, bins=0, method='sd'):
    """
    Identifies snips that are classed as noisy due to exceeding a threshold based on background.

    Parameters
    ----------
    data : List or 1D array of Floats
        Data stream from entire session.
    background_events : List
        Timestamps from which background snips will be made.
    t2sMap : List of floats, optional
        Time-to-samples map. The default is [].
    fs : Float, optional
        Sampling frequency. The default is 1.
    bins : Int, optional
        Number of bins to be used for snips. The default is 0.
    method : String ('sd' or 'sum'), optional
        Method of calculating noise - standard deviation or sum. The default is 'sd'.

    Returns
    -------
    bgMAD : Float
        Median absoluate deviation of background trials.

    """
    
    bgSnips, _ = snipper(data, background, t2sMap=t2sMap, fs=fs, bins=bins)
    
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
    noiseindex : List of Boolean values
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