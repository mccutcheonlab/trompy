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

from test_helpers import create_gcamp_kernel, create_data_stream, create_stream_with_events

# %matplotlib inline

np.random.seed(222)

def test_output():
    data = np.random.random(10000)
    events = np.random.randint(1000, high=90000, size=5) / 10
    output, pps = tp.snipper(data, events)
    assert np.shape(output) == (5, 30)

    events[2] = np.nan
    events[3] = np.inf
    output, _ = tp.snipper(data, events)
    assert np.shape(output) == (3, 30) #checks that nans and infs removed

def test_peaks():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()
    output, _ = tp.snipper(simulated_gcamp, events, fs=fs, adjustBaseline = False)

    # With seed=222, deterministic peak positions are at indices 1233 and 1342
    peak_positions = [np.argmax(trace) for trace in output]
    assert peak_positions == [1233, 1342], f"Peak positions {peak_positions} don't match expected [1233, 1342]"

def test_adjust_baseline():
    np.random.seed(222)
    simulated_gcamp, events, fs = create_stream_with_events()

    x = np.arange(len(simulated_gcamp))
    low_freq_signal = np.sin(x/100000)
    simulated_gcamp_with_drift = simulated_gcamp + low_freq_signal
    
    output, _ = tp.snipper(simulated_gcamp_with_drift, events, fs=fs, adjust_baseline = True)

    for trace in output:
        # Baseline adjustment should be very precise (essentially zero mean)
        np.testing.assert_allclose(np.mean(trace[:1234]), 0.0, atol=0.05)  # Tightened from 0.3
        # Both traces should have positive values at index 1234 (first is ~7.09, second is ~0.55)
        assert trace[1234] > 0.5 or trace[1234] > 0.5  # Just check signal is reasonable

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
            np.testing.assert_allclose(baseline, 0.0, atol=0.05)  # Tightened - baseline should be near zero
            # Minimum post-baseline value across all configs is ~2.498
            assert np.mean(output[:,(pre+1)*10]) > 2.4, f"Value {np.mean(output[:,(pre+1)*10]):.3f} too low for pre={pre}"

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
        
def test_diff_baselines():
    data = np.random.random(10000)
    data[5000:] = data[5000:]+5
    events = [4000, 5005, 9000]
    output, _ = tp.snipper(data, events, baseline_length=10, trial_length=20, fs=1, adjust_baseline=False)
    #print(output)
    # assert np.shape(output) == (5, 30)

    data = data + 10
    output, _ = tp.snipper(data, events, baseline_length=[10, 5], trial_length=20, fs=1, adjust_baseline=True)
    bl = output[1][:5]
    non_bl = output[1][5:10]
    
    assert np.mean(bl)+4 < np.mean(non_bl)
    print(output)
    print(np.mean(bl), np.mean(non_bl))
    
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
