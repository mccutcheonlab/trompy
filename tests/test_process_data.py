# %%
"""
Created on Wed Mar 23 13:57:05 2022

@author: jmc010
"""
import pytest
import numpy as np
import trompy as tp
import matplotlib.pyplot as plt
from test_helpers import (create_gcamp_kernel, create_data_stream, 
                          add_noise, add_drift, double_exponential)

# %matplotlib inline

np.random.seed(222)

def test_length():
    n_samples = 12000  # Further reduced with lower fs for faster testing
    fs = 123.456  # Reduced from 1017.324
    n_events = 5  # Reduced proportionally

    data1 = create_data_stream(n_samples, fs, create_gcamp_kernel, [])
    data2 = create_data_stream(n_samples, fs, create_gcamp_kernel, [])

    processed = tp.processdata(data1, data2)

    assert len(processed) == n_samples

def test_df():
    n_samples = 12000  # Further reduced with lower fs for faster testing
    fs = 123.456  # Reduced from 1017.324

    events = np.arange(1000, 6000, 400) / 100  # Events between 10-60 seconds

    simulated_gcamp = create_data_stream(n_samples, fs, create_gcamp_kernel, events)

    noise = add_noise(np.zeros(n_samples))

    t=np.arange(n_samples)
    simulated_405 = double_exponential(t, 400, 2e6, 100, 1e5) + noise
    simulated_gcamp_plus_noise = simulated_gcamp + double_exponential(t, 300, 2e6, 75, 1e5) + noise

    processed_lerner = tp.processdata(simulated_gcamp_plus_noise, simulated_405, method="lerner", normalize=False)
    # processed_konanur = tp.processdata(simulated_gcamp_plus_noise, simulated_405, method="konanur", normalize=False)

    f, ax = plt.subplots(nrows=4)
    ax[0].plot(simulated_405)
    ax[1].plot(simulated_gcamp_plus_noise)
    ax[2].plot(processed_lerner)
    # ax[3].plot(processed_konanur)

    event_indices = [int(event*fs) for event in events]

    assert all(event > 0 for event in processed_lerner[event_indices])
    # Exact expected value at index 1234 is ~3.147593
    np.testing.assert_allclose(processed_lerner[1234], 3.147593, rtol=0.01)  # 1% tolerance
    # Check that processed signal has reasonable peak values at events
    assert np.max(processed_lerner[event_indices]) > 3

    # TODO improve konanur function and checking, maybe using real data to examine freqs and fits
    # TODO check with reduced sampling frequencies

def future_test_process_data_with_drift():
    n_samples = 600000
    fs = 1017.324
    n_events = 150

    events = np.random.randint(6000, high=54000, size=n_events) / 100

    simulated_gcamp = create_data_stream(n_samples, fs, create_gcamp_kernel, events)
    
    noise = add_noise(np.zeros(n_samples))

    t=np.arange(n_samples)
    simulated_405 = double_exponential(t, 400, 2e6, 100, 1e5) + noise
    simulated_gcamp_plus_noise = simulated_gcamp + double_exponential(t, 300, 2e6, 75, 1e5) + noise

    f, ax = plt.subplots(nrows=3)
    ax[0].plot(simulated_405)
    ax[1].plot(simulated_gcamp_plus_noise)

    processed_signal = tp.processdata(simulated_gcamp_plus_noise, simulated_405, method="lerner", normalize=False)

    ax[2].plot(processed_signal)
    simulated_405_plus_drift = add_drift(simulated_405)
    simulated_gcamp_plus_drift = add_drift(simulated_gcamp_plus_noise)

    processed_signal2 = tp.processdata(simulated_405_plus_drift, simulated_gcamp_plus_drift, method="lerner", normalize=False)
    
    f, ax = plt.subplots(nrows=3)
    ax[0].plot(simulated_405_plus_drift)
    ax[1].plot(simulated_gcamp_plus_drift)
    ax[2].plot(processed_signal2)

if __name__ == "__main__":
    # test_process_data()
    test_length()
    test_df()
    
# %%

# %%
