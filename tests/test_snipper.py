# -*- coding: utf-8 -*-
# %%
"""
Created on Wed Mar 23 13:57:05 2022

@author: jmc010
"""
from email.mime import base
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

def create_stream_with_events(n_samples=600000, fs=1017.324, kernel_process=create_gcamp_kernel, n_events=3):

    events = np.random.randint(6000, high=54000, size=n_events) / 100
    simulated_gcamp = create_data_stream(n_samples, fs, create_gcamp_kernel, events)

    return simulated_gcamp, events, fs

def test_peaks():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()
    output, _ = tp.snipper(simulated_gcamp, events, fs=fs, adjustBaseline = False)

    for trace in output:
        assert np.argmax(trace) == 10173

def test_adjust_baseline():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    x = np.arange(len(simulated_gcamp))
    low_freq_signal = np.sin(x/100000)
    simulated_gcamp_with_drift = simulated_gcamp + low_freq_signal
    
    output, _ = tp.snipper(simulated_gcamp_with_drift, events, fs=fs, adjust_baseline = True)

    for trace in output:
        np.testing.assert_allclose(np.mean(trace[:10000]), 0.0, atol=0.1)
        assert trace[10173] > 0

def test_bins():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    for n_bins in [30]:
        output, _ = tp.snipper(simulated_gcamp, events, fs=fs, adjust_baseline = True, bins=n_bins)
        scaling_factor = n_bins/30

        assert np.shape(output)[1] == n_bins

        for trace in output:
            print(trace[int(scaling_factor*11)])
            np.testing.assert_allclose(np.mean(trace[:int(scaling_factor*10)]), 0.0, atol=0.1)
            assert trace[int(scaling_factor*11)] > 2

def test_trial_length():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    f, ax = plt.subplots()
    for pre in [1, 5, 10]:
        for length in [12, 15, 20, 30]:
            output, _ = tp.snipper(simulated_gcamp, events, fs=fs, adjust_baseline = True,
                                    baseline_length=pre,
                                    trial_length=length,
                                    bins=length*10)
            baseline = np.mean(output[:,:pre*10])
            np.testing.assert_allclose(baseline, 0.0, atol=0.1)
            assert np.mean(output[:,(pre+1)*10]) > 4

def test_no_events():
    np.random.seed(222)
    data = np.random.random(10000)
    events=[]

    with pytest.raises(Exception):
        _, _ = tp.snipper(data, events, fs=10)

def test_overlap():
    np.random.seed(222)

    for fs in [10, 100, 1017.234]:
        data = np.random.random(int(120*fs))
        events=[1, 60, 119]

        output, _ = tp.snipper(data, events, fs=fs)
        assert len(output) == 1

# TODO: check with varied fs

if __name__ == "__main__":
    # test_output()
    # test_peaks()
    # test_adjust_baseline() 
    # test_bins()
    # test_trial_length()
    # test_no_events()
    test_overlap()


# %%
