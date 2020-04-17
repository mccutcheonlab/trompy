# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:12:17 2020

@author: admin
"""

import numpy as np
import os

def remcheck(val, range1, range2):
    """
    Checks whether value is within range of two decimals.

    Parameters
    ----------
    val : Float
        Value to be checked.
    range1 : Float
        Decimal 1.
    range2 : Float
        Decimal 2.

    Returns
    -------
    bool
        Result of check.

    """
    # function checks whether value is within range of two decimels
    if (range1 < range2):
        if (val > range1) and (val < range2):
            return True
        else:
            return False
    else:
        if (val > range1) or (val < range2):
            return True
        else:
            return False
    
def random_array(dims,n, multiplier = 10):
    """
    Creates random array of values. Useful for checking plot functions, e.g. barscatter.

    Parameters
    ----------
    dims : Int
        Number of dimensions.
    n : Int
        Number of data points in each data set.
    multiplier : Int or Float, optional
        Value to multiply random data points by. The default is 10.

    Returns
    -------
    data : List of lists
        Random data array as a list of lists with appropriate dimensions.

    """
    
    data = []
    import numpy as np
    try:
        if len(dims) == 2:
            data = np.empty((dims), dtype=np.object)        
            for i in range(np.shape(data)[0]):
                for j in range(np.shape(data)[1]):
                    data[i][j] = np.random.random((n))*multiplier
        elif len(dims) > 2:
            print('Too many dimensions!')
            return
        
        elif len(dims) == 1:
            data = np.empty((dims), dtype=np.object)
            for i,j in enumerate(data):
                data[i] = np.random.random((n))*multiplier
    except TypeError:
        print('Dimensions need to be in a list or matrix')
        return

    return data

def getuserhome():
    path = os.environ['USERPROFILE']
    return path

def flatten_list(listoflists):
    try:
        flat_list = [item for sublist in listoflists for item in sublist]
        return flat_list
    except:
        print('Cannot flatten list. Maybe is in the wrong format. Returning empty list.')
        return []
    
def discrete2continuous(onset, offset=[], nSamples=[], fs=[]):
    """
    Takes timestamp data (e.g. licks) that can include offsets as well as onsets,
    and returns a digital on/off array (y) as well as the x output. The number 
    of samples (nSamples) and sample frequency (fs) can be input or if they are
    not (default) it will attempt to calculate them based on the timestamp data.
    It has not been fully stress-tested yet.

    Parameters
    ----------
    onset : List or 1D array
        Timestamps of onsets.
    offset : List or 1D array, optional
        Timestamps of offsets. The default is [].
    nSamples : Int, optional
        Number of samples. The default is [].
    fs : Float, optional
        Sample frequency. The default is [].

    Returns
    -------
    outputx : List
        x values for y-array.
    outputy : List
        On / off array.

    """

    try:
        fs = int(fs)
    except TypeError:
        isis = np.diff(onset)
        fs = int(1 / (min(isis)/2)) 
    
    if len(nSamples) == 0:
        nSamples = int(fs*max(onset))    
    
    outputx = np.linspace(0, nSamples/fs, nSamples)
    outputy = np.zeros(len(outputx))
    
    if len(offset) == 0:
        for on in onset:
            idx = (np.abs(outputx - on)).argmin()
            outputy[idx] = 1
    else:
        for i, on in enumerate(onset):
            start = (np.abs(outputx - on)).argmin()
            stop = (np.abs(outputx - offset[i])).argmin()
            outputy[start:stop] = 1

    return outputx, outputy

def findpercentilevalue(data, percentile):

    if (0 < percentile) and (percentile <= 1):
        position = int(percentile*len(data))
    else:
        print('Value for percentile must be between 0 and 1')
        return

    sorteddata = np.sort(data)
    value = sorteddata[position-1]
    
    return value
