# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:09:57 2020

@author: admin
"""

import numpy as np
import scipy.stats as stats

def sidakcorr(pval, ncomps=3):
    corr_p = 1-((1-pval)**ncomps)   
    return corr_p

def mean_and_sem(data, verbose=False):
    mean = np.mean(data)
    sem = np.std(data)/(np.sqrt(np.size(data)))
    if verbose:
        print(f"Mean: {mean}, SEM: {sem}")
    return (mean, sem)

def bonferroni_corrected_ttest(data1, data2, comps=3, string_prefix="", verbose=False):
    t, p = stats.ttest_rel(data1, data2)
    corr_p = p*comps
    if verbose:
        print(f"{string_prefix}t-stat: {np.abs(t):03.1f}, corrected p: {corr_p:03.4f}")
    return (t, corr_p)