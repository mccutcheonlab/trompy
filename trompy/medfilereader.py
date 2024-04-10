# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:12:10 2020

@author: James Edgar McCutcheon
"""
from pathlib import Path
import numpy as np
import string
import datetime

def medfilereader(filename, vars_to_extract='all', session_to_extract=1, verbose=False, remove_var_header=False, dictionary_output=False, **kwargs):
    """
    Reads in Med Associates file stored as single column and returns variables as lists.

    Parameters
    ----------
    filename : str
        File to be read in.
    vars_to_extract : str or list of str, optional
        Variables to extract from the file. Default is 'all'.
    session_to_extract : int, optional
        Specifies the session to extract from the file. Default is 1.
    verbose : bool, optional
        If True, prints statements with file information. Default is False.
    remove_var_header : bool, optional
        If True, removes the first value in each variable array. Useful when negative numbers are used as markers to signal array start. Default is False.
    dictionary_output : bool, optional
        If True, returns the variables as a dictionary with variable names as keys. Default is False.
    **kwargs : dict, optional
        Additional keyword arguments.

    Returns
    -------
    vars_to_return : list or dict
        Variables extracted from the medfile. If dictionary_output is False, returns a list of lists of numbers (int or float). If dictionary_output is True, returns a dictionary with variable names as keys and lists of numbers as values.
    """
    # Function code goes here
    pass
def medfilereader(filename, vars_to_extract = 'all',
                  session_to_extract = 1,
                  verbose = False,
                  remove_var_header = False,
                  dictionary_output = False,
                  **kwargs):
    
    """Reads in Med Associates file stored as single column and returns variables as lists.
    
    Parameters
    ----------
    filename : str
        File to be read in.
    varsToExtract : str or list of str, optional
        (e.g. ['a', 'b', 'f']), default is 'all'
    sessionToExtract : int, optional
        Can be specified for situations in which more than one session is included in a single file. Deafult is 1.
    verbose : bool, optional
        Prints statements with file information. Default is False.
    remove_var_header : bool, optional
        Removes first value in array, useful when negative numbers are used as markers to signal array start. Default is False.
    
    Returns
    -------
    varsToReturn : list of lists of numbers (int or float)
        Variables extracted from medfile as lists or a list of lists ('all')
    """
    if 'varsToExtract' in kwargs:
        vars_to_extract = kwargs['varsToExtract']

    if 'sessionToExtract' in kwargs:
        vars_to_extract = kwargs['sessionToExtract']

    if vars_to_extract == 'all':
        num_vars_to_extract = np.arange(0,26)
    else:
        num_vars_to_extract = [ord(x.lower())-97 for x in vars_to_extract]
    
    f = open(Path(filename), 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    if session_to_extract > len(matches):
        print('Session ' + str(session_to_extract) + ' does not exist.')
    if verbose == True:
        print('There are ' + str(len(matches)) + ' sessions in ' + filename)
        print('Analyzing session ' + str(session_to_extract))
    
    varstart = matches[session_to_extract - 1]
    medvars = [[] for n in range(26)]
    
    k = int(varstart + 27)
    for i in range(26):
        medvarsN = int(datarows[varstart + i + 1])
        
        medvars[i] = datarows[k:k + int(medvarsN)]
        k = k + medvarsN
        
    if remove_var_header == True:
        vars_to_return = [medvars[i][1:] for i in num_vars_to_extract]
    else:
        vars_to_return = [medvars[i] for i in num_vars_to_extract]

    if len(vars_to_return) == 1:
        vars_to_return = vars_to_return[0]

    if dictionary_output == True:
        num_vars_to_extract = [chr(x + 97) for x in num_vars_to_extract]
        vars_to_return = {num_vars_to_extract[i]: vars_to_return[i] for i in range(len(vars_to_return))}

    return vars_to_return

def isnumeric(s):
    """Converts strings into numbers (floats)

    Parameters
    ----------
    s : any
    
    Returns
    -------
    x : float
    """
    
    try:
        x = float(s)
        return x
    except ValueError:
        return float('nan')
    
def checknsessions(filename):
    '''Helper function for medfilereader that checks how many sessions in medfile'''
    
    f = open(filename, 'r')
    f.seek(0)
    filerows = f.readlines()[8:]
    datarows = [isnumeric(x) for x in filerows]
    matches = [i for i,x in enumerate(datarows) if x == 0.3]
    return matches

def tstamp_to_tdate(timestamp, fmt):
    '''Converts timestamp in string format into datetime object'''
    
    try:
        return datetime.datetime.strptime(timestamp, fmt)
    except ValueError:
        return

def medfilereader_licks(filename,
                  sessionToExtract = 1,
                  verbose = False,
                  remove_var_header = True):
    
    """Reads in Med Associates file stored as single column and returns variables as lists.
    
    Parameters
    ----------
    filename : str
        File to be read in.
    sessionToExtract : int, optional
        Can be specified for situations in which more than one session is included in a single file. Deafult is 1.
    verbose : bool, optional
        Prints statements with file information. Default is False.
    remove_var_header : bool, optional
        Removes first value in array, useful when negative numbers are used as markers to signal array start. Default is False.
    
    Returns
    -------
    medvars : list of lists of numbers (int or float)
        Variables extracted from medfile as lists or a list of lists ('all')
    """
    
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

if __name__ == '__main__':
    print('Testing functions')
    import trompy as tp
    filename = Path("C:/Users/jmc010/Github/trompy/tests/test_data/!2016-08-12_09h33m.Subject 14")

    data = tp.medfilereader(filename, vars_to_extract=["e", "x"], dictionary_output=True)
    print(len(data))
    print(data.keys())

    for key, val in data.items():
        print(key, len(val))
