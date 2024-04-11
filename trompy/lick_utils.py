# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:40:05 2020

@author: James Edgar McCutcheon
"""
from pathlib import Path
from trompy.lickcalc import Lickcalc

def lickCalc(licks, offset = [], burstThreshold = 0.5, runThreshold = 10,
             ignorelongilis=True, longlickThreshold=0.3, minburstlength=1,
             minrunlength=1,
             binsize=60, histDensity = False):
    """
    Calcuates various parameters for a train of licking data including bursting 
    parameters and returns as a dictionary. Legacy function that returns a dictionary.

    Parameters
    ----------
    licks : List or 1D array
        Timestamps of licks (onsets). Expects in seconds. If given in ms then other
        parameters should be changed, e.g. `burstThreshold`.
    offset : List or 1D array, optional
        Timestamps of lick offsets. The default is [].
    burstThreshold : Float, optional
        Interlick threshold (in seconds) for defining bursts. The default is 0.5.
    runThreshold : Float or Int, optional
        Number of seconds separating runs of licks. The default is 10.
    ignorelongilis : Boolean, optional
        Removes ILIs > `burstThreshold` from calcuations. Useful for calculating
        intraburst frequency. The default is True.
    longlickThreshold : Float, optional
        Threshold (in seconds) for long licks. The default is 0.3.
    minburstlength : Int, optional
        Minimum number of licks to be considered a burst. Common values are either 1 or 3. The default is 1.
    binsize : Int or Float, optional
        Size of bins for constructing histogram. The default is 60.
    histDensity : Boolean, optional
        Converts histogram into a density plot rather than absolute. The default is False.

    Returns
    -------
    lickdata, a dictionary with the following keys
    'licklength' : List of floats
        Lick lengths (empty if offset times not given)
    'longlicks' : List of floats
        Licks that are greater than `longlickThreshold`
    'licks' : List of floats
        Lick onset times
    'ilis' : List of floats
        Interlick intervals
    'freq' : Float
        Mean frequency (in Hz) of intraburst licking
    'total' : Int
        Number of licks
    'bStart' : List of floats
        Timestamps of licks that start a burst
    'bInd' : List of ints
        Indices of licks that start a burst
    'bEnd' : List of floats
        Timestamps of licks that end a burst
    'bLicks' : List of ints
        Numbers of licks in each burst
    'bTime' : Array of floats
        Duration (in seconds) of each burst
    'bMean' : Float
        Mean number of licks in all bursts
    'bMean-first3' : Float
        Mean number of licks in first three bursts
    'IBIs' : List of floats
        Interburst intervals
    'rStart' : List of floats
        Timestamps for licks that start a run. Runs designated by `runThreshold`
    'rInd' : List of ints
        Indices of licks that start a run
    'rEnd' : List of ints
        Timestamps of licks that end a run
    'rLicks' : List of ints
        Number of licks per run
    'rTime' : Array of floats
        Duration (in seconds) of each run
    'rNum' : Int
        Number of runs
    'weib_alpha' : Float
        Alpha parameter from fitted Weibull function
    'weib_beta' : Float
        Beta parameter from fitted Weibull function
    'weib_rsq' : Float
        Rsquared value from fitted Weibull function
    'burstprob' : List
        xdata and ydata of cumulative burst probability
    'hist' : List
        Histogram of licks over time
    
    Notes
    ----------
    For more information on appropriate thresholds (e.g. numbers of licks or interlick intervals) see Naneix et al (2019) for more info.
        https://doi.org/10.1016/j.neuroscience.2019.10.036
    
    For more information on the Weibull function used to model burst probability see Davis (1998) DOI: 10.1152/ajpregu.1996.270.4.R793
    """

    lickdata = Lickcalc(licks=licks,
                        offset=offset,
                        burst_threshold=burstThreshold,
                        longlick_threshold=longlickThreshold,
                        min_burst_length=minburstlength,
                        ignorelongilis=ignorelongilis,
                        run_threshold=runThreshold,
                        min_run_length=minrunlength,
                        binsize=binsize,
                        hist_density=histDensity)
    
    if lickdata.weibull_params is None:
        lickdata.weibull_params = [None, None, None]
    
    return {'licklength' : lickdata.licklength,
            'longlicks' : lickdata.longlicks,
            'licks' : lickdata.licks,
            'ilis' : lickdata.ilis,
            'freq' : lickdata.intraburst_freq,
            'total' : lickdata.total,
            'bStart' : lickdata.burst_start,
            'bInd' : lickdata.burst_inds,
            'bEnd' : lickdata.burst_end,
            'bLicks' : lickdata.burst_licks,
            'bNum': lickdata.burst_number,
            'bTime' : lickdata.burst_lengths,
            'bMean' : lickdata.burst_mean,
            'bMean-first3' : lickdata.burst_mean_first3,
            'IBIs' : lickdata.interburst_intervals,
            'rStart' : lickdata.runs_start,
            'rInd' : lickdata.runs_inds,
            'rEnd' : lickdata.runs_end,
            'rLicks' : lickdata.runs_licks,
            'rTime' : lickdata.runs_length,
            'rNum' : lickdata.runs_number,
            'weib_alpha' : lickdata.weibull_params[0],
            'weib_beta' : lickdata.weibull_params[1],
            'weib_rsq' : lickdata.weibull_params[2],
            'burstprob' : lickdata.burst_prob,
            'hist' : lickdata.histogram
            }

if __name__ == '__main__':
    print('Testing functions')
    import trompy as tp
    filename = Path("C:/Github/trompy/tests/test_data/03_W.med")

    data = tp.medfilereader(filename, vars_to_extract=["e", "f"], remove_var_header=True)

    lickdata = lickCalc(data[0], offset=data[1], minburstlength=1)
    
    print(lickdata["rEnd"])

    # print(lickdata['freq'])



