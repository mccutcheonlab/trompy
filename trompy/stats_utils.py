# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:09:57 2020

@author: James Edgar McCutcheon
"""

import numpy as np
from scipy.stats import t, ttest_rel
from scipy.special import betainc

def sidakcorr(pval, ncomps=3):
    """ Performs Sidak correction on a given p-value"""
    
    corr_p = 1-((1-pval)**ncomps)   
    return corr_p

def mean_and_sem(data, verbose=False):
    """ Calculates mean and standard error of the mean"""
    
    mean = np.mean(data)
    sem = np.std(data)/(np.sqrt(np.size(data)))
    if verbose:
        print(f"Mean: {mean}, SEM: {sem}")
    return (mean, sem)

def bonferroni_corrected_ttest(data1, data2, comps=3, string_prefix="", verbose=False):
    """ Performs a bonferroni corrected t-test"""
    
    t, p = ttest_rel(data1, data2)
    corr_p = p*comps
    if verbose:
        print("{}t-stat: {:03.1f}, corrected p: {:03.4f}".format(string_prefix, np.abs(t), corr_p))
    return (t, corr_p)

## Functions required for calculations of ANOVA statistics
# sum of squares of treatment / regression
def ssr(data):
    sums = []
    for group in data:
        sums.append(len(group) * (np.mean(group) - np.mean(data))**2)
        
    return np.sum(sums)

# sum of squares error
def sse(data):
    sums = []
    for group in data:
        sums.append(np.sum([(x-np.mean(group))**2 for x in group]))
    
    return np.sum(sums)

def dfr(data):
    return np.shape(data)[0] - 1
    
def dfe(data):
    if np.ndim(data) == 1:
        return np.sum([len(x) for x in data]) - len(data)
    elif np.ndim(data) == 2:
        return np.size(data) - np.shape(data)[0]

def msr(data):
    return ssr(data) / dfr(data)

def mse(data):
    return sse(data) / dfe(data)

def fval(data):
    return msr(data) / mse(data)

def pval(data):
    """
    Finds p-value associated with combination of F and df values.
    
    Uses incomplete betfunction from scipy. Also discussed here:
    https://stackoverflow.com/questions/38113120/calculate-f-distribution-p-values-in-python
    """
    F, df1, df2 = fval(data), dfr(data), dfe(data)
    return 1 - betainc(.5*df1, .5*df2, float(df1)*F/(df1*F+df2))

def lsd(data, groups, alpha=0.025):
    return t.ppf(1-alpha, dfe(data)) * np.sqrt(mse(data) * (1/len(data[groups[0]]) + 1/len(data[groups[1]])))

def lsd_pval(data, groups):
    """
    Returns two-tailed p-value for LSD (least significant difference) posthoc tests.
    
    Args
    data : Numpy array
        Data to be tested, m x n array where first dimension are groups (between) and second dim is subjects (within)
    groups : List or tuple
        Two integers specifying groups to be compared.
        
    Returns
        
    """
    if np.ndim(data) == 1:
        gp1 = data[groups[0]]
        gp2 = data[groups[1]]
    elif np.ndim(data) == 2:
        gp1 = data[groups[0],:]
        gp2 = data[groups[1],:]
    else:
        print("Input data has too many dimensions. Exiting.")
        return
    
    diff = np.abs(np.mean(gp1) - np.mean(gp2))
    
    tval = diff / np.sqrt(mse(data) * (1/len(gp1) + 1/len(gp2)))
    pval = t.sf(np.abs(tval), dfe(data))*2
    
    return pval