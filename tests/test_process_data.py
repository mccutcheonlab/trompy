# %%
"""
Created on Wed Mar 23 13:57:05 2022

@author: jmc010
"""
from audioop import add
import pytest
import numpy as np
import trompy as tp
import matplotlib.pyplot as plt

%matplotlib inline

np.random.seed(222)

def create_gcamp_kernel(t, tau=2.6):
    K = (1/tau)*(np.exp(-t/tau))
    return K

def create_data_stream(n_samples, fs, kernel_process, events, add_noise=True):

    # to create gcamp kernel
    x=np.arange(0, 30, 1/fs)
    kernel=[kernel_process(t) for t in x]

    # converts events into sample numbers
    events_in_samples = [int(event*fs) for event in events]

    # creates stream
    stream = np.zeros(n_samples- len(kernel) + 1 )
    stream[events_in_samples] = [np.abs(np.random.normal(scale=20)) for e in range(len(events))]

    simulated_data_stream = np.convolve(stream, kernel, "full")

    if add_noise:
        simulated_data_stream = simulated_data_stream + np.random.normal(0,0.1,n_samples)

    return simulated_data_stream

def add_noise(data_stream, magnitude=0.5):
    return data_stream + np.random.normal(0,magnitude,len(data_stream))

def add_drift(data_stream, freq=0.0001, magnitude=10):
    x = np.arange(len(data_stream))
    low_freq_signal = magnitude * np.sin(x/(1/freq))
    
    return data_stream + low_freq_signal

def double_exponential(t, a1, b1, a2, b2):
    return a1 * np.exp(-t/b1) + a2 * np.exp(-t/b2)

def test_length():
    n_samples = 600000
    fs = 1017.324
    n_events = 150

    data1 = create_data_stream(n_samples, fs, create_gcamp_kernel, [])
    data2 = create_data_stream(n_samples, fs, create_gcamp_kernel, [])

    processed = tp.processdata(data1, data2)

    assert len(processed) == n_samples

def test_process_data():
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

    processed_signal2 = tp.processdata(simulated_405_plus_drift, simulated_gcamp_plus_drift, method="konanur", normalize=False)
    
    f, ax = plt.subplots(nrows=3)
    ax[0].plot(simulated_405_plus_drift)
    ax[1].plot(simulated_gcamp_plus_drift)
    ax[2].plot(processed_signal2)

if __name__ == "__main__":
    test_process_data()
    # test_length()
    
# %%

# %%
