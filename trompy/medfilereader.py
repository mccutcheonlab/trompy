# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:12:10 2020

@author: admin
"""

import numpy as np

def medfilereader(filename, varsToExtract = 'all',
                  sessionToExtract = 1,
                  verbose = False,
                  remove_var_header = False):
    
    """
    Reads in Med Associates file stored as single column and returns variables as lists.
    Args:
        filename - file to be read in
        varsToExtract - to be provided as list of strings (e.g. ['a', 'b', 'f']), default is 'all'
        sessionToExtract - 1 is default, but can be specified for situations in which more than one session is included in a single file   
        verbose - prints statements with file information, False is default
        remove_var_header - removes first value in array, useful when negative numbers are used as markers to signal array start, False is default
        
    Returns:
        Variables extracted from medfile as lists or a list of lists ('all')
    """  

    if varsToExtract == 'all':
        numVarsToExtract = np.arange(0,26)
    else:
        numVarsToExtract = [ord(x)-97 for x in varsToExtract]
    
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    if sessionToExtract > len(matches):
        print('Session ' + str(sessionToExtract) + ' does not exist.')
    if verbose == True:
        print('There are ' + str(len(matches)) + ' sessions in ' + filename)
        print('Analyzing session ' + str(sessionToExtract))
    
    varstart = matches[sessionToExtract - 1]
    medvars = [[] for n in range(26)]
    
    k = int(varstart + 27)
    for i in range(26):
        medvarsN = int(datarows[varstart + i + 1])
        
        medvars[i] = datarows[k:k + int(medvarsN)]
        k = k + medvarsN
        
    if remove_var_header == True:
        varsToReturn = [medvars[i][1:] for i in numVarsToExtract]
    else:
        varsToReturn = [medvars[i] for i in numVarsToExtract]

    if np.shape(varsToReturn)[0] == 1:
        varsToReturn = varsToReturn[0]
    return varsToReturn

def isnumeric(s):
    """ Converts strings into numbers (floats) """
    try:
        x = float(s)
        return x
    except ValueError:
        return float('nan')
    
def checknsessions(filename):
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    return matches

def tstamp_to_tdate(timestamp, fmt):
    try:
        return datetime.datetime.strptime(timestamp, fmt)
    except ValueError:
        return

def medfilereader_licks(filename,
                  sessionToExtract = 1,
                  verbose = False,
                  remove_var_header = True):
    '''Gets lick data from Med Associates file.'''
    
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    if sessionToExtract > len(matches):
        print('Session ' + str(sessionToExtract) + ' does not exist.')
    if verbose == True:
        print('There are ' + str(len(matches)) + ' sessions in ' + filename)
        print('Analyzing session ' + str(sessionToExtract))
    
    varstart = matches[sessionToExtract - 1]    
    medvars = {}
   
    k = int(varstart + 27)
    for i in range(26):
        medvarsN = int(datarows[varstart + i + 1])
        if medvarsN > 1:
            medvars[string.ascii_uppercase[i]] = datarows[k:k + int(medvarsN)]
        k = k + medvarsN
    
    if remove_var_header == True:
        for val in medvars.values():
            val.pop(0)

    return medvars