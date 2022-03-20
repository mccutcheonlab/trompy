# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:12:17 2020

@author: James Edgar McCutcheon
"""

import numpy as np
import os

def remcheck(val, range1, range2):
    """ Checks whether value is within range of two decimals.

    Parameters
    ----------
    val : float
        Value to be checked.
    range1 : float
        Decimal 1.
    range2 : float
        Decimal 2.

    Returns
    -------
    bool
        Result of check.

    """
    
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
    """ Creates random array of values. Useful for checking plot functions, e.g. barscatter.

    Parameters
    ----------
    dims : int
        Number of dimensions.
    n : int
        Number of data points in each data set.
    multiplier : int or float, optional
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
    """ Returns path to user's home directory"""
    
    path = os.environ['USERPROFILE']
    return path

def flatten_list(listoflists):
    """ Flattens list of lists into a 1D list"""
    
    try:
        flat_list = [item for sublist in listoflists for item in sublist]
        return flat_list
    except:
        print('Cannot flatten list. Maybe is in the wrong format. Returning empty list.')
        return []
    
def discrete2continuous(onset, offset=[], nSamples=[], fs=[]):
    """
    Takes timestamp data (e.g. licks) that can include offsets as well as onsets,
    and returns a digital on/off array (y) as well as the x output.

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
        
    Notes
    -------
    The number of samples (nSamples) and sample frequency (fs) can be input or if they are not (default) it will attempt to calculate them based on the timestamp data.
    Not been fully stress-tested yet.

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
    """ Finds percentile value in a specified data set.
    
    Parameters
    ------------
    data : list or 1D array
    percentile : float
        Must be between 0 and 1.
    
    Returns
    ---------
    value : int
        Value in data set closest to percentile
    
    """

    if (0 < percentile) and (percentile <= 1):
        position = int(percentile*len(data))
    else:
        print('Value for percentile must be between 0 and 1')
        return

    sorteddata = np.sort(data)
    value = sorteddata[position-1]
    
    return value

def logical_subset(data, logical, condition=True):
    """ Returns logical subset."""
    
    if condition:
        return [d for d, L in zip(data, logical) if L]
    else:
        return [d for d, L in zip(data, logical) if not L]
    
def find_overlap(i1, i2, if_none=None):
    """
    Finds the amount of overlap between two intervals. Useful for looking at
    time series when you only have onset and offset times.

    Parameters
    ----------
    i1 : Tuple or list of floats or integers with length=2
        Interval 1.
    i2 : Tuple or list of floats or integers with length=2
        Interval 2.
    if_none : Any, optional
        Value that will be returned if intervals do not overlap. The default is None.

    Returns
    -------
    Float, if there is overlap between intervals. Otherwise, depends on value
    of if_none variable but default is None
        Amount of overlap.

    """
    if (len(i1) != 2) or (len(i2) !=2):
        print("Intervals cannot be compared as they do not include start and stop.")
        return
    
    if (i1[1] < i2[0]) or (i1[0] > i2[1]):
        return if_none
    else:
        return min(i1[1], i2[1]) - max(i1[0], i2[0])

def download_data(url):
    """
    Downloads zipped data from a remote URL and unzips. Unzipped data
    is in a new directory in the current working directory called 'data'.
    
    Parameters
    ------------
    url : String with url for data to be retrieved from
    
    """
    import os
    print(os.getcwd())
    if not os.path.exists('data.zip'):
        import urllib.request
        import sys
        import time

        print('downloading data...')

        def reporthook(count, block_size, total_size):
            global start_time
            if count == 0:
                start_time = time.time()
                return
            duration = time.time() - start_time
            progress_size = int(count * block_size)
            if duration > 0:
                speed = int(progress_size / (1024 * duration))
                percent = min(int(count * block_size * 100 / total_size), 100)
                sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds elapsed" %
                                (percent, progress_size / (1024 * 1024), speed, duration))
                sys.stdout.flush()

        urllib.request.urlretrieve(url, '.\\data.zip', reporthook)

    try:
        print('unzipping data...')
        import zipfile
        zip_ref = zipfile.ZipFile('data.zip', 'r')
        zip_ref.extractall('.\\data')
        zip_ref.close()
        os.remove('data.zip')
    except:
        print('problem with zip, downloading again')
        os.remove('data.zip')
        return download_demo_data()
    
    print("Datafiles ready")