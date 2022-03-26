# -*- coding: utf-8 -*-
# %%
"""
Created on Wed Mar 23 13:57:05 2022

@author: jmc010
"""
import pytest
import numpy as np
import trompy as tp
import matplotlib.pyplot as plt

# %matplotlib inline

np.random.seed(222)

def test_output():
    data = np.random.random(10000)
    events = np.random.randint(1000, high=90000, size=5) / 10
    output, pps = tp.snipper(data, events)
    assert np.shape(output) == (5, 30)

    events[2] = np.nan
    events[3] = np.inf
    output, pps = tp.snipper(data, events)
    assert np.shape(output) == (3, 30) #checks that nans and infs removed

def create_gcamp_kernel(t, tau=2.6):
    K = (1/tau)*(np.exp(-t/tau))
    return K

def create_data_stream(n_samples, fs, kernel_process, events):

    # to create gcamp kernel
    x=np.arange(0, 30, 1/fs)
    kernel=[kernel_process(t) for t in x]

    # converts events into sample numbers
    events_in_samples = [int(event*fs) for event in events]

    # creates stream
    stream = np.zeros(n_samples- len(kernel) + 1 )
    stream[events_in_samples] = [np.abs(np.random.normal(scale=20)) for e in range(len(events))]

    simulated_data_stream = np.convolve(stream, kernel, "full")

    return simulated_data_stream

def test_peaks():
    n_samples = 600000
    fs = 1017.324
    n_events = 3

    events = np.random.randint(6000, high=54000, size=n_events) / 100

    simulated_gcamp = create_data_stream(n_samples, fs, create_gcamp_kernel, events)

    output, pps = tp.snipper(simulated_gcamp, events, fs=fs, adjustBaseline = False)

    for trace in output:
        assert np.argmax(trace) == 10170

def test_adjust_baseline():
    n_samples = 600000
    fs = 1017.324
    n_events = 3

    events = np.random.randint(6000, high=54000, size=n_events) / 100

    simulated_gcamp = create_data_stream(n_samples, fs, create_gcamp_kernel, events)

    x = np.arange(len(simulated_gcamp))
    low_freq_signal = np.sin(x/100000)
    simulated_gcamp_with_drift = simulated_gcamp + low_freq_signal

    output, pps = tp.snipper(simulated_gcamp_with_drift, events, fs=fs, adjustBaseline = True)

    for trace in output:
        np.testing.assert_allclose(trace[10000], 0.0, atol=0.1)
        assert trace[10170] > 0

# TODO: check for triallength and pretrial
# TODO: check for bins
# TODO: check with varied fs and event numbers (e.g. 0 events)
# TODO: check with events that overlap the end of the file

if __name__ == "__main__":
    test_output()
    test_peaks()
    test_adjust_baseline() 





# %%
