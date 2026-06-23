# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:40:05 2020

@author: James Edgar McCutcheon
"""
from pathlib import Path
import numpy as np
import warnings
from trompy.lickcalc import Lickcalc


def _compute_time_divisions(lickdata, n_divisions, session_length=None):
    """Compute statistics for time-based divisions"""
    if not len(lickdata.licks) or n_divisions <= 0:
        return []
        
    # Determine session boundaries
    start_time = lickdata.licks[0]
    if session_length is not None:
        end_time = start_time + session_length
    else:
        end_time = lickdata.licks[-1]
    
    duration_per_division = (end_time - start_time) / n_divisions
    divisions = []
    
    for i in range(n_divisions):
        div_start = start_time + i * duration_per_division
        div_end = start_time + (i + 1) * duration_per_division
        
        # Get licks within this time range
        if i == n_divisions - 1:  # Last division includes end boundary
            segment_licks = [t for t in lickdata.licks if div_start <= t <= div_end]
        else:
            segment_licks = [t for t in lickdata.licks if div_start <= t < div_end]
        
        # Get corresponding offsets if available
        segment_offsets = _get_corresponding_offsets(lickdata, segment_licks)
        
        # Calculate statistics for this segment
        stats = _calculate_segment_stats(lickdata, segment_licks, segment_offsets)
        
        # Add division metadata
        stats.update({
            'division_type': 'time',
            'division_number': i + 1,
            'start_time': div_start,
            'end_time': div_end,
            'duration': div_end - div_start
        })
        
        divisions.append(stats)
    
    return divisions


def _compute_burst_divisions(lickdata, n_divisions):
    """Compute statistics for burst-based divisions"""
    if not len(lickdata.licks) or n_divisions <= 0:
        return []
        
    if lickdata.burst_number == 0:
        # Return empty divisions if no bursts
        return [_create_empty_burst_division(lickdata, i+1) for i in range(n_divisions)]
    
    # Calculate bursts per division
    bursts_per_division = max(1, lickdata.burst_number // n_divisions)
    divisions = []
    
    for i in range(n_divisions):
        start_burst = i * bursts_per_division
        
        if i == n_divisions - 1:
            # Last division gets all remaining bursts
            end_burst = lickdata.burst_number
        else:
            end_burst = (i + 1) * bursts_per_division
        
        # Get licks for this burst range
        segment_licks = _get_licks_for_burst_range(lickdata, start_burst, end_burst)
        
        # Get corresponding offsets if available
        segment_offsets = _get_corresponding_offsets(lickdata, segment_licks)
        
        # Calculate statistics for this segment
        stats = _calculate_segment_stats(lickdata, segment_licks, segment_offsets)
        
        # Calculate time boundaries for burst division
        if segment_licks:
            div_start_time = min(segment_licks)
            div_end_time = max(segment_licks)
        else:
            # Estimate times for empty divisions
            session_duration = lickdata.licks[-1] - lickdata.licks[0] if len(lickdata.licks) > 1 else 0
            start_proportion = start_burst / max(lickdata.burst_number, 1)
            end_proportion = end_burst / max(lickdata.burst_number, 1)
            div_start_time = lickdata.licks[0] + start_proportion * session_duration
            div_end_time = lickdata.licks[0] + end_proportion * session_duration
        
        # Add division metadata
        stats.update({
            'division_type': 'burst',
            'division_number': i + 1,
            'start_burst': start_burst,
            'end_burst': end_burst,
            'start_time': div_start_time,
            'end_time': div_end_time,
            'duration': div_end_time - div_start_time
        })
        
        divisions.append(stats)
    
    return divisions


def _get_licks_for_burst_range(lickdata, start_burst, end_burst):
    """Extract licks that belong to a specific range of bursts"""
    if start_burst >= end_burst or lickdata.burst_number == 0:
        return []
    
    # Ensure valid burst range
    start_burst = max(0, min(start_burst, lickdata.burst_number))
    end_burst = max(start_burst, min(end_burst, lickdata.burst_number))
    
    if start_burst == end_burst:
        return []
    
    # Extract the time boundaries for our burst range
    if start_burst < len(lickdata.burst_start):
        range_start_time = float(lickdata.burst_start[start_burst])
    else:
        range_start_time = lickdata.licks[0]
    
    if end_burst - 1 < len(lickdata.burst_end):
        range_end_time = float(lickdata.burst_end[end_burst - 1])
    else:
        range_end_time = lickdata.licks[-1]
    
    # Return licks within this time range
    return [t for t in lickdata.licks if range_start_time <= t <= range_end_time]


def _get_corresponding_offsets(lickdata, segment_licks):
    """Get corresponding offset times for a segment of licks"""
    if lickdata.offset is None or not segment_licks:
        return []
    
    # Use numpy boolean indexing for O(n) performance instead of O(n²) .index() loop
    segment_licks_array = np.array(segment_licks)
    mask = np.isin(lickdata.licks, segment_licks_array)
    segment_indices = np.where(mask)[0]
    
    # Return corresponding offsets
    valid_indices = segment_indices[segment_indices < len(lickdata.offset)]
    if len(valid_indices) > 0:
        return lickdata.offset[valid_indices].tolist()
    
    return []


def _calculate_segment_stats(lickdata, segment_licks, segment_offsets):
    """Calculate comprehensive statistics for a segment of licks"""
    if not segment_licks:
        return {
            'total_licks': 0,
            'intraburst_freq': np.nan,
            'n_bursts': 0,
            'mean_licks_per_burst': np.nan,
            'weibull_alpha': None,
            'weibull_beta': None,
            'weibull_rsq': None,
            'n_long_licks': 0,
            'max_lick_duration': np.nan
        }
    
    # Create a temporary Lickcalc object for this segment
    try:
        segment_calc = Lickcalc(
            licks=segment_licks,
            offset=segment_offsets,
            burst_threshold=lickdata.burst_threshold,
            longlick_threshold=lickdata.longlick_threshold,
            min_burst_length=lickdata.min_burst_length,
            ignorelongilis=lickdata.ignorelongilis,
            remove_longlicks=lickdata.remove_longlicks,
            only_return_first_n_bursts=lickdata.only_return_first_n_bursts,
            run_threshold=lickdata.run_threshold,
            min_run_length=lickdata.min_run_length,
            binsize=lickdata.binsize,
            hist_density=lickdata.hist_density
        )
        
        # Extract statistics
        stats = {
            'total_licks': segment_calc.total,
            'intraburst_freq': segment_calc.intraburst_freq,
            'n_bursts': segment_calc.burst_number,
            'mean_licks_per_burst': segment_calc.burst_mean,
            'weibull_alpha': segment_calc.weibull_params[0] if segment_calc.weibull_params else None,
            'weibull_beta': segment_calc.weibull_params[1] if segment_calc.weibull_params else None,
            'weibull_rsq': segment_calc.weibull_params[2] if segment_calc.weibull_params else None,
            'n_long_licks': len(segment_calc.longlicks) if segment_calc.longlicks is not None else 0,
            'max_lick_duration': np.max(segment_calc.licklength) if segment_calc.licklength is not None and len(segment_calc.licklength) > 0 else np.nan
        }
        
    except Exception:
        # Fallback for problematic segments
        stats = {
            'total_licks': len(segment_licks),
            'intraburst_freq': np.nan,
            'n_bursts': 0,
            'mean_licks_per_burst': np.nan,
            'weibull_alpha': None,
            'weibull_beta': None,
            'weibull_rsq': None,
            'n_long_licks': 0,
            'max_lick_duration': np.nan
        }
    
    return stats


def _create_empty_burst_division(lickdata, division_number):
    """Create an empty burst division for cases with no bursts"""
    return {
        'division_type': 'burst',
        'division_number': division_number,
        'start_burst': 0,
        'end_burst': 0,
        'start_time': lickdata.licks[0] if len(lickdata.licks) > 0 else 0,
        'end_time': lickdata.licks[-1] if len(lickdata.licks) > 0 else 0,
        'duration': 0,
        'total_licks': 0,
        'intraburst_freq': np.nan,
        'n_bursts': 0,
        'mean_licks_per_burst': np.nan,
        'weibull_alpha': None,
        'weibull_beta': None,
        'weibull_rsq': None,
        'n_long_licks': 0,
        'max_lick_duration': np.nan
    }

def lickcalc(licks, offset = [], burstThreshold = 0.5, runThreshold = 10,
             ignorelongilis=True, longlickThreshold=0.3, minburstlength=1,
             minrunlength=1,
             binsize=60, histDensity = False, remove_longlicks=False,
             only_return_first_n_bursts=False,
             time_divisions=None, burst_divisions=None, session_length=None):
    """
    Calculates various parameters for a train of licking data including bursting 
    parameters and returns as a dictionary. Legacy function that returns a dictionary.

    Parameters
    ----------
    licks : List or 1D array
        Timestamps of licks (onsets). Expects in seconds. If given in ms then other
        parameters should be changed, e.g. `burstThreshold`.
    offset : List or 1D array, optional
        Timestamps of lick offsets. The default is [].
    burstThreshold : Float, optional
        Interlick threshold (in seconds) for defining bursts. The default is 0.5.
    runThreshold : Float or Int, optional
        Number of seconds separating runs of licks. The default is 10.
    ignorelongilis : Boolean, optional
        Removes ILIs > `burstThreshold` from calcuations. Useful for calculating
        intraburst frequency. The default is True.
    longlickThreshold : Float, optional
        Threshold (in seconds) for long licks. The default is 0.3.
    minburstlength : Int, optional
        Minimum number of licks to be considered a burst. Common values are either 1 or 3. The default is 1.
    binsize : Int or Float, optional
        Size of bins for constructing histogram. The default is 60.
    histDensity : Boolean, optional
        Converts histogram into a density plot rather than absolute. The default is False.
    remove_longlicks : Boolean, optional
        If True, removes longlicks (duration > longlickThreshold) from all calculations. The default is False.
    only_return_first_n_bursts : Int or Boolean, optional
        If an integer N, only returns statistics for the first N bursts. If fewer than N bursts exist, all are returned without error. The default is False.
    time_divisions : Int, optional
        Number of equal time divisions to create for temporal analysis. The default is None.
    burst_divisions : Int, optional
        Number of divisions based on burst count distribution. The default is None.
    session_length : Float, optional
        Total session length in seconds (for time divisions). If None, uses actual data duration. The default is None.

    Returns
    -------
    lickdata, a dictionary with the following keys
    'licklength' : List of floats or None
        Lick lengths (None if offset times not given)
    'licklength_mode' : Float or None
        Modal (most common) lick duration (None if offset times not given)
    'longlicks' : List of floats or None
        Licks that are greater than `longlickThreshold` (None if none found)
    'licks' : List of floats
        Lick onset times
    'ilis' : List of floats
        Interlick intervals
    'freq' : Float or None
        Mean frequency (in Hz) of intraburst licking (None if no bursts)
    'intraburst_mode' : Float or None
        Modal inter-lick interval within bursts (None if no bursts)
    'total' : Int
        Number of licks
    'bStart' : List of floats
        Timestamps of licks that start a burst
    'bInd' : List of ints
        Indices of licks that start a burst
    'bEnd' : List of floats
        Timestamps of licks that end a burst
    'bLicks' : List of ints
        Numbers of licks in each burst
    'bNum' : Int
        Total number of bursts
    'bTime' : List of floats
        Duration (in seconds) of each burst
    'bMean' : Float or None
        Mean number of licks in all bursts (None if no bursts)
    'bMean-first3' : Float or None
        Mean number of licks in first three bursts (None if fewer than 3 bursts)
    'IBIs' : List of floats or None
        Interburst intervals (None if no bursts)
    'rStart' : List of floats
        Timestamps for licks that start a run (runs designated by `runThreshold`)
    'rInd' : List of ints
        Indices of licks that start a run
    'rEnd' : List of floats
        Timestamps of licks that end a run
    'rLicks' : List of ints
        Number of licks per run
    'rTime' : List of floats
        Duration (in seconds) of each run
    'rNum' : Int
        Number of runs
    'weib_alpha' : Float or None
        Alpha parameter from fitted Weibull function (None if no bursts or fit failed)
    'weib_beta' : Float or None
        Beta parameter from fitted Weibull function (None if no bursts or fit failed)
    'weib_rsq' : Float or None
        R-squared value from fitted Weibull function (None if no bursts or fit failed)
    'burstprob' : Tuple or None
        (xdata, ydata) of cumulative burst probability (None if no bursts)
    'hist' : List
        Histogram of licks over time
    'time_divisions' : List of dicts, optional
        Time-based division analysis results (if time_divisions specified).
        Each dict contains:
            - division_type : str ('time')
            - division_number : int (1-indexed)
            - start_time : float, end_time : float (time boundaries)
            - duration : float (division duration in seconds)
            - total_licks : int
            - n_bursts : int (number of bursts in division)
            - mean_licks_per_burst : float
            - intraburst_freq : float
            - weibull_alpha, weibull_beta, weibull_rsq : float or None
            - n_long_licks : int
            - max_lick_duration : float
    'burst_divisions' : List of dicts, optional
        Burst-based division analysis results (if burst_divisions specified).
        Each dict contains same statistics as time_divisions, plus:
            - start_burst : int, end_burst : int (burst indices)
            - start_time : float, end_time : float (estimated time boundaries)

    Notes
    ----------
    For more information on appropriate thresholds (e.g. numbers of licks or interlick intervals) see Naneix et al (2019).
        https://doi.org/10.1016/j.neuroscience.2019.10.036

    For more information on the Weibull function used to model burst probability see Davis (1998).
        DOI: 10.1152/ajpregu.1996.270.4.R793

    Examples
    --------
    Basic usage (backward compatible):
    >>> results = lickcalc(lick_times)

    With temporal divisions:
    >>> results = lickcalc(lick_times, time_divisions=4)
    >>> for div in results['time_divisions']:
    ...     print(f"Division {div['division_number']}: {div['total_licks']} licks")

    With both time and burst divisions:
    >>> results = lickcalc(lick_times, time_divisions=3, burst_divisions=2)

    With session length and divisions:
    >>> results = lickcalc(lick_times, time_divisions=4, session_length=600)
    """

    lickdata = Lickcalc(licks=licks,
                        offset=offset,
                        burst_threshold=burstThreshold,
                        longlick_threshold=longlickThreshold,
                        min_burst_length=minburstlength,
                        ignorelongilis=ignorelongilis,
                        remove_longlicks=remove_longlicks,
                        only_return_first_n_bursts=only_return_first_n_bursts,
                        run_threshold=runThreshold,
                        min_run_length=minrunlength,
                        binsize=binsize,
                        hist_density=histDensity)
    
    if lickdata.weibull_params is None:
        lickdata.weibull_params = [None, None, None]
    
    # Standard results dictionary
    results = {'licklength' : lickdata.licklength,
               'licklength_mode' : lickdata.licklength_mode,
            'longlicks' : lickdata.longlicks,
            'licks' : lickdata.licks,
            'ilis' : lickdata.ilis,
            'freq' : lickdata.intraburst_freq,
            'intraburst_mode' : lickdata.intraburst_mode,
            'total' : lickdata.total,
            'bStart' : lickdata.burst_start,
            'bInd' : lickdata.burst_inds,
            'bEnd' : lickdata.burst_end,
            'bLicks' : lickdata.burst_licks,
            'bNum': lickdata.burst_number,
            'bTime' : lickdata.burst_lengths,
            'bMean' : lickdata.burst_mean,
            'bMean-first3' : lickdata.burst_mean_first3,
            'IBIs' : lickdata.interburst_intervals,    
            'rStart' : lickdata.runs_start,
            'rInd' : lickdata.runs_inds,
            'rEnd' : lickdata.runs_end,
            'rLicks' : lickdata.runs_licks,
            'rTime' : lickdata.runs_length,
            'rNum' : lickdata.runs_number,
            'weib_alpha' : lickdata.weibull_params[0],
            'weib_beta' : lickdata.weibull_params[1],
            'weib_rsq' : lickdata.weibull_params[2],
            'burstprob' : lickdata.burst_prob,
            'hist' : lickdata.histogram
            }
    
    # Add division analysis if requested
    if time_divisions is not None and time_divisions > 0:
        results['time_divisions'] = _compute_time_divisions(
            lickdata, time_divisions, session_length
        )
    
    if burst_divisions is not None and burst_divisions > 0:
        results['burst_divisions'] = _compute_burst_divisions(
            lickdata, burst_divisions
        )
    
    return results


def lickCalc(licks, offset = [], burstThreshold = 0.5, runThreshold = 10,
             ignorelongilis=True, longlickThreshold=0.3, minburstlength=1,
             minrunlength=1,
             binsize=60, histDensity = False, remove_longlicks=False,
             only_return_first_n_bursts=False,
             time_divisions=None, burst_divisions=None, session_length=None):
    """
    Deprecated: Use `lickcalc` (lowercase) instead.
    
    This function is maintained for backward compatibility but will be removed
    in a future version. Please update your code to use `lickcalc`.
    """
    warnings.warn(
        "lickCalc is deprecated and will be removed in a future version. "
        "Please use lickcalc (all lowercase) instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return lickcalc(licks, offset, burstThreshold, runThreshold,
                   ignorelongilis, longlickThreshold, minburstlength,
                   minrunlength, binsize, histDensity, remove_longlicks,
                   only_return_first_n_bursts, time_divisions, burst_divisions,
                   session_length)



