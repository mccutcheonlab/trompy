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
    snipper = tp.Snipper(data, events, pre=10, post=20)
    output = snipper.get_snips()
    assert np.shape(output) == (5, 30)

    events[2] = np.nan
    events[3] = np.inf
    snipper = tp.Snipper(data, events, pre=10, post=20)
    output = snipper.get_snips()
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

def create_stream_with_events(n_samples=600000, fs=1017.321, kernel_process=create_gcamp_kernel, n_events=3):

    events = np.random.randint(6000, high=54000, size=n_events) / 100
    simulated_gcamp = create_data_stream(n_samples, fs, create_gcamp_kernel, events)

    return simulated_gcamp, events, fs

def test_peaks():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()
    snipper = tp.Snipper(simulated_gcamp, events, fs=fs, adjustbaseline = False)
    output = snipper.get_snips()

    for trace in output:
        assert np.argmax(trace) == 10174

def test_adjust_baseline():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    x = np.arange(len(simulated_gcamp))
    low_freq_signal = np.sin(x/100000)
    simulated_gcamp_with_drift = simulated_gcamp + low_freq_signal
    
    snipper = tp.Snipper(simulated_gcamp_with_drift, events, fs=fs, adjustbaseline = True)
    output = snipper.get_snips()

    for trace in output:
        np.testing.assert_allclose(np.mean(trace[:10000]), 0.0, atol=0.1)
        assert trace[10174] > 0

def test_bins():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    for binlength in [0.01, 0.1, 0.2, 0.5, 1, 5]:
        snipper = tp.Snipper(simulated_gcamp, events, fs=fs, adjustbaseline = True, binlength=binlength)
        output = snipper.get_snips()
        
        scaling_factor = 1/binlength
        assert np.shape(output)[1] == int(scaling_factor * 30)

        for trace in output:
            print(trace[int(scaling_factor*11)])
            np.testing.assert_allclose(np.mean(trace[:int(scaling_factor*10)]), 0.0, atol=0.1)
            assert trace[int(scaling_factor*11)] > 2

def test_trial_length():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    for pre in [1, 5, 10]:
        for length in [12, 15, 20, 30]:
            snipper = tp.Snipper(simulated_gcamp, events, fs=fs, adjustbaseline = True,
                                 pre=pre,
                                 post=length-pre,
                                 binlength=0.1)

            output = snipper.get_snips()

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

        snipper = tp.Snipper(data, events, fs=fs)
        output = snipper.get_snips()
        assert len(output) == 1
        
def test_diff_baselines():
    data = np.random.random(10000)
    data[5000:] = data[5000:]+5
    events = [4000, 5005, 9000]
    
    snipper = tp.Snipper(data, events, fs=1, baselinelength=10, post=10, adjust_baseline=False)
    output = snipper.get_snips()

    assert np.shape(output) == (3, 20)

    data = data + 10
    snipper = tp.Snipper(data, events, fs=1, baselinelength=[10, 5], post=10, adjust_baseline=True)
    output = snipper.get_snips()
    
    bl = output[1][:5]
    non_bl = output[1][5:10]
    
    assert np.mean(bl)+4 < np.mean(non_bl)
    
    # add check to see what happens if incorrect number of values given for baseline or if trial length is too short


# TODO: check with varied fs

if __name__ == "__main__":
    # test_output()
    # test_peaks()
    test_diff_baselines()
    # test_adjust_baseline() 
    # test_bins()
    # test_trial_length()
    # test_no_events()
    # test_overlap()


# %%
