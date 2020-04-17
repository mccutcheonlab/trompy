# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:12:17 2020

@author: admin
"""

import numpy as np

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