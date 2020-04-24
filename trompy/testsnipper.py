# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:56:36 2020

@author: admin
"""
import numpy as np
from trompy import *
import tdt

import matplotlib.pyplot as plt

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
        return snippererror()
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
        return snippererror()
    
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
        bgMAD = findnoise(data, makerandomevents(120, max(t2sMap)-120),
                              t2sMap=t2sMap, fs=fs, bins=bins,
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
    
    return output

def snippererror():
    print('Returning empty snips dictionary.')
    output = {}
    output['blue'] = []
    output['uv'] = []
    output['filt'] = []
    output['filt_z'] = []
    output['filt_avg'] = []
    output['filt_avg_z'] = []
    output['noise'] = []
    output['peak'] = []
    output['latency'] = []
    
    return output

def snipper(data, timelock, fs = 1, preTrial=10, trialLength=30,
                 adjustBaseline = True,
                 bins = 0, **kwargs):
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
    preTrial : Int, optional
        Number of seconds to include before event. The default is 10.
    trialLength : Int, optional
        Total length (in seconds) of each snip. The default is 30.
    adjustBaseline : Bool, optional
        When True divides all data points in each snip by mean of points occurring before event. The default is True.
    bins : Int, optional
        Number of bins to divide trial length into. The default is 0. If set at default
        of 0 then no binning will occur.

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
    if 't2sMap' in kwargs.keys():
        for x in timelock:
            event.append(np.searchsorted(kwargs['t2sMap'], x, side="left"))
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
            snips = snips[:i]
            avgBaseline = avgBaseline[:i]
            nSnips = i
            break # Exits for loop

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

folder = "C:\\Test Data\\data\\FiPho-180416\\"
tmp = tdt.read_block(folder)
data = tmp.streams._4654.data
fs = tmp.streams._4654.fs
events = tmp.epocs.PtAB.onset

t2sMap = time2samples(data, fs)




snips = mastersnipper(data, data, data, fs, events,
                      snipfs=10, trialLength=30, preTrial=10,
                      hullabaloo='trig')

print(np.shape(snips['blue']))
avg = np.mean(snips['blue'], axis=0)

# fig, ax = plt.subplots()
# ax.plot(np.mean(snips['blue'], axis=0))
# plt.show()