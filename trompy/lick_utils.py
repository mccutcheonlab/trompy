# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:40:05 2020

@author: James Edgar McCutcheon
"""
from pathlib import Path
import numpy as np
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
    
    # Find indices of segment licks in original lick list
    segment_indices = []
    licks_list = list(lickdata.licks)
    
    for seg_lick in segment_licks:
        try:
            idx = licks_list.index(seg_lick)
            segment_indices.append(idx)
        except ValueError:
            continue
    
    # Return corresponding offsets
    if segment_indices and len(lickdata.offset) > max(segment_indices):
        return [lickdata.offset[i] for i in segment_indices if i < len(lickdata.offset)]
    
    return []


def _calculate_segment_stats(lickdata, segment_licks, segment_offsets):
    """Calculate comprehensive statistics for a segment of licks"""
    if not segment_licks:
        return {
            'total_licks': 0,
            'intraburst_freq': np.nan,
            'n_bursts': 0,
            'mean_licks_per_burst': np.nan,
            'weibull_alpha': np.nan,
            'weibull_beta': np.nan,
            'weibull_rsq': np.nan,
            'n_long_licks': np.nan,
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
            'weibull_alpha': segment_calc.weibull_params[0] if segment_calc.weibull_params else np.nan,
            'weibull_beta': segment_calc.weibull_params[1] if segment_calc.weibull_params else np.nan,
            'weibull_rsq': segment_calc.weibull_params[2] if segment_calc.weibull_params else np.nan,
            'n_long_licks': len(segment_calc.longlicks) if segment_calc.longlicks else np.nan,
            'max_lick_duration': np.max(segment_calc.licklength) if segment_calc.licklength is not None and len(segment_calc.licklength) > 0 else np.nan
        }
        
    except Exception:
        # Fallback for problematic segments
        stats = {
            'total_licks': len(segment_licks),
            'intraburst_freq': np.nan,
            'n_bursts': 0,
            'mean_licks_per_burst': np.nan,
            'weibull_alpha': np.nan,
            'weibull_beta': np.nan,
            'weibull_rsq': np.nan,
            'n_long_licks': np.nan,
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
        'weibull_alpha': np.nan,
        'weibull_beta': np.nan,
        'weibull_rsq': np.nan,
        'n_long_licks': np.nan,
        'max_lick_duration': np.nan
    }

def lickCalc(licks, offset = [], burstThreshold = 0.5, runThreshold = 10,
             ignorelongilis=True, longlickThreshold=0.3, minburstlength=1,
             minrunlength=1,
             binsize=60, histDensity = False, time_divisions=None, 
             burst_divisions=None, session_length=None):
    """
    Calcuates various parameters for a train of licking data including bursting 
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
    time_divisions : Int, optional
        Number of equal time divisions to create for temporal analysis. The default is None.
    burst_divisions : Int, optional
        Number of divisions based on burst count distribution. The default is None.
    session_length : Float, optional
        Total session length in seconds (for time divisions). If None, uses actual data duration. The default is None.

    Returns
    -------
    lickdata, a dictionary with the following keys
    'licklength' : List of floats
        Lick lengths (empty if offset times not given)
    'longlicks' : List of floats
        Licks that are greater than `longlickThreshold`
    'licks' : List of floats
        Lick onset times
    'ilis' : List of floats
        Interlick intervals
    'freq' : Float
        Mean frequency (in Hz) of intraburst licking
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
    'bTime' : Array of floats
        Duration (in seconds) of each burst
    'bMean' : Float
        Mean number of licks in all bursts
    'bMean-first3' : Float
        Mean number of licks in first three bursts
    'IBIs' : List of floats
        Interburst intervals
    'rStart' : List of floats
        Timestamps for licks that start a run. Runs designated by `runThreshold`
    'rInd' : List of ints
        Indices of licks that start a run
    'rEnd' : List of ints
        Timestamps of licks that end a run
    'rLicks' : List of ints
        Number of licks per run
    'rTime' : Array of floats
        Duration (in seconds) of each run
    'rNum' : Int
        Number of runs
    'weib_alpha' : Float
        Alpha parameter from fitted Weibull function
    'weib_beta' : Float
        Beta parameter from fitted Weibull function
    'weib_rsq' : Float
        Rsquared value from fitted Weibull function
    'burstprob' : List
        xdata and ydata of cumulative burst probability
    'hist' : List
        Histogram of licks over time
    'time_divisions' : List of dicts, optional
        Time-based division analysis results (if time_divisions specified)
    'burst_divisions' : List of dicts, optional
        Burst-based division analysis results (if burst_divisions specified)
    
    Notes
    ----------
    For more information on appropriate thresholds (e.g. numbers of licks or interlick intervals) see Naneix et al (2019) for more info.
        https://doi.org/10.1016/j.neuroscience.2019.10.036
    
    For more information on the Weibull function used to model burst probability see Davis (1998) DOI: 10.1152/ajpregu.1996.270.4.R793
    
    Examples
    --------
    Basic usage (backward compatible):
    >>> results = lickCalc(lick_times)
    
    With temporal divisions:
    >>> results = lickCalc(lick_times, time_divisions=4)
    >>> for div in results['time_divisions']:
    ...     print(f"Division {div['division_number']}: {div['total_licks']} licks")
    
    With both time and burst divisions:
    >>> results = lickCalc(lick_times, time_divisions=3, burst_divisions=2)
    """

    lickdata = Lickcalc(licks=licks,
                        offset=offset,
                        burst_threshold=burstThreshold,
                        longlick_threshold=longlickThreshold,
                        min_burst_length=minburstlength,
                        ignorelongilis=ignorelongilis,
                        run_threshold=runThreshold,
                        min_run_length=minrunlength,
                        binsize=binsize,
                        hist_density=histDensity)
    
    if lickdata.weibull_params is None:
        lickdata.weibull_params = [None, None, None]
    
    # Standard results dictionary
    results = {'licklength' : lickdata.licklength,
            'longlicks' : lickdata.longlicks,
            'licks' : lickdata.licks,
            'ilis' : lickdata.ilis,
            'freq' : lickdata.intraburst_freq,
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





