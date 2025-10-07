"""
Shared test utilities for trompy tests.

This module contains helper functions used across multiple test files
to generate simulated GCaMP signals and data streams.
"""
import numpy as np


def create_gcamp_kernel(t, tau=2.6):
    """Create a GCaMP calcium indicator kernel with exponential decay.
    
    Parameters
    ----------
    t : float or array
        Time values
    tau : float, optional
        Time constant for exponential decay (default: 2.6)
    
    Returns
    -------
    K : float or array
        Kernel values at time t
    """
    K = (1/tau) * (np.exp(-t/tau))
    return K


def create_data_stream(n_samples, fs, kernel_process, events, add_noise=False):
    """Create a simulated data stream with calcium transients at specified events.
    
    Parameters
    ----------
    n_samples : int
        Number of samples in the output stream
    fs : float
        Sampling frequency in Hz
    kernel_process : callable
        Function that generates the calcium indicator kernel (e.g., create_gcamp_kernel)
    events : array-like
        Times (in seconds) where calcium transients should occur
    add_noise : bool, optional
        If True, adds Gaussian noise to the signal (default: False)
    
    Returns
    -------
    simulated_data_stream : ndarray
        Simulated data stream with calcium transients
    """
    # Create kernel
    x = np.arange(0, 30, 1/fs)
    kernel = [kernel_process(t) for t in x]

    # Convert events from seconds to sample indices
    events_in_samples = [int(event*fs) for event in events]

    # Create sparse event stream
    stream = np.zeros(n_samples - len(kernel) + 1)
    # Generate event amplitudes with baseline offset (+1) for all events
    # Note: This matches the original test_process_data.py behavior
    stream[events_in_samples] = [np.abs(np.random.normal(scale=20)) + 1 for e in range(len(events))]

    # Convolve with kernel to create calcium transients
    simulated_data_stream = np.convolve(stream, kernel, "full")

    if add_noise:
        simulated_data_stream = simulated_data_stream + np.random.normal(0, 0.1, n_samples)

    return simulated_data_stream


def create_stream_with_events(n_samples=8000, fs=123.456, kernel_process=create_gcamp_kernel, 
                               n_events=3):
    """Create a simulated GCaMP data stream with random events.
    
    Convenience function that generates random event times and creates a data stream.
    
    Parameters
    ----------
    n_samples : int, optional
        Number of samples in the output stream (default: 8000)
    fs : float, optional
        Sampling frequency in Hz (default: 123.456)
    kernel_process : callable, optional
        Function that generates the calcium indicator kernel (default: create_gcamp_kernel)
    n_events : int, optional
        Number of random events to generate (default: 3)
    
    Returns
    -------
    simulated_gcamp : ndarray
        Simulated GCaMP data stream
    events : ndarray
        Times (in seconds) of the generated events
    fs : float
        Sampling frequency (returned for convenience)
    """
    # Generate random event times between 3-20 seconds
    events = np.random.randint(300, high=2000, size=n_events) / 100
    simulated_gcamp = create_data_stream(n_samples, fs, kernel_process, events)

    return simulated_gcamp, events, fs


def add_noise(data_stream, magnitude=0.5):
    """Add Gaussian noise to a data stream.
    
    Parameters
    ----------
    data_stream : array-like
        Input data stream
    magnitude : float, optional
        Standard deviation of the Gaussian noise (default: 0.5)
    
    Returns
    -------
    ndarray
        Data stream with added noise
    """
    return data_stream + np.random.normal(0, magnitude, len(data_stream))


def add_drift(data_stream, freq=0.0001, magnitude=10):
    """Add low-frequency sinusoidal drift to a data stream.
    
    Parameters
    ----------
    data_stream : array-like
        Input data stream
    freq : float, optional
        Frequency of the drift signal (default: 0.0001)
    magnitude : float, optional
        Amplitude of the drift signal (default: 10)
    
    Returns
    -------
    ndarray
        Data stream with added drift
    """
    x = np.arange(len(data_stream))
    low_freq_signal = magnitude * np.sin(x / (1/freq))
    
    return data_stream + low_freq_signal


def double_exponential(t, a1, b1, a2, b2):
    """Double exponential function for modeling photobleaching/decay.
    
    Parameters
    ----------
    t : float or array
        Time values
    a1 : float
        Amplitude of first exponential component
    b1 : float
        Time constant of first exponential component
    a2 : float
        Amplitude of second exponential component
    b2 : float
        Time constant of second exponential component
    
    Returns
    -------
    float or array
        Sum of two exponential decays
    """
    return a1 * np.exp(-t/b1) + a2 * np.exp(-t/b2)
