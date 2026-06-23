
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import scipy.optimize as opt

class Lickcalc:
    """
    Analyzes licking behavior data to compute bursts, runs, and related statistics.

    This class processes raw lick onset and offset times to extract comprehensive
    behavioral metrics including burst structure, lick runs, inter-lick intervals,
    and burst probability distributions.

    Parameters
    ----------
    licks : array_like
        Lick onset times (in seconds or arbitrary time units).
    offset : array_like, optional
        Lick offset times. Required for lick length analysis.
    longlick_threshold : float, default 0.3
        Duration threshold (seconds) above which licks are classified as "long".
    burst_threshold : float, default 0.5
        Inter-lick interval threshold (seconds) for burst boundaries.
    min_burst_length : int, default 1
        Minimum number of licks to define a burst. Shorter bursts are filtered.
    run_threshold : float, default 10
        Time threshold (seconds) for lick run boundaries.
    min_run_length : int, default 1
        Minimum number of licks to define a run. Shorter runs are filtered.
    binsize : int, default 60
        Bin size (seconds) for histogram computation.
    hist_density : bool, default False
        If True, normalize histogram to density. If False, return counts.
    ignorelongilis : bool, default False
        If True, exclude inter-lick intervals > burst_threshold from ILI calculations.
    remove_longlicks : bool, default False
        If True, filter out licks exceeding longlick_threshold before analysis.
    only_return_first_n_bursts : int or False, default False
        If an integer, keep only the first N bursts. Useful for fixed-duration sessions.

    Attributes (Burst Analysis)
    ---------------------------
    burst_inds : list
        Indices where bursts begin.
    burst_licks : list
        Number of licks per burst.
    burst_start : list
        Onset time of each burst.
    burst_end : list
        Offset time of each burst (last lick in burst).
    burst_lengths : list
        Duration of each burst (burst_end - burst_start).
    burst_number : int
        Total number of bursts.
    burst_mean : float
        Mean licks per burst.
    burst_mean_first3 : float
        Mean licks for first 3 bursts.
    intraburst_freq : float
        Mean frequency (licks/sec) of licks within bursts.
    intraburst_mode : float
        Modal inter-lick interval within bursts.
    interburst_intervals : array_like
        Time gaps between consecutive bursts.
    burst_prob : tuple
        (x, y) cumulative burst probability distribution [Davis et al. 1996].
    weibull_params : tuple or None
        (alpha, beta, r_squared) Weibull fit to burst probability.

    Attributes (Run Analysis)
    -------------------------
    runs : list of array_like
        Arrays of lick times for each run.
    runs_start : list
        Onset time of each run.
    runs_inds : list
        Indices where runs begin.
    runs_end : list
        Offset time of each run (last lick in run).
    runs_licks : list
        Number of licks per run.
    runs_length : list
        Duration of each run (runs_end - runs_start).
    runs_number : int
        Total number of runs.

    Attributes (Lick-level Metrics)
    --------------------------------
    licks : array_like
        Processed lick onset times (filtered if remove_longlicks=True).
    offset : array_like or None
        Processed lick offset times (filtered if remove_longlicks=True).
    total : int
        Total number of licks.
    licklength : array_like or None
        Duration of each lick (offset - onset).
    licklength_mode : float or None
        Modal lick duration.
    longlicks : array_like or None
        Lick durations exceeding longlick_threshold.
    ilis : array_like
        Inter-lick intervals (differences between consecutive lick onsets).
    ilis_in_bursts : DataFrame
        Detailed breakdown of inter-lick intervals within bursts.

    Attributes (Other)
    -------------------
    histogram : array_like
        Histogram of lick times using binsize.

    Methods
    -------
    get_burst_mean(number=None) : float
        Mean licks per burst, optionally for first N bursts.
    keep_first_n_bursts(n) : None
        Truncate burst data to keep only first N bursts.
    remove_short_bursts() : None
        Filter out bursts with fewer licks than min_burst_length.
    remove_short_runs() : None
        Filter out runs with fewer licks than min_run_length.
    get_ilis_in_bursts() : DataFrame
        Compute inter-lick intervals with burst context and surrounding gaps.

    Examples
    --------
    >>> licks = np.array([0.5, 0.6, 0.7, 5.0, 5.1, 5.2])
    >>> offsets = np.array([0.52, 0.62, 0.72, 5.02, 5.12, 5.22])
    >>> calc = Lickcalc(licks=licks, offset=offsets, burst_threshold=0.5, run_threshold=2.0)
    >>> print(f"Bursts: {calc.burst_number}, Licks: {calc.total}")
    """
    def __init__(self, **kwargs):
        ## Set default parameters
        self.longlick_threshold = kwargs.get('longlick_threshold', 0.3)
        self.burst_threshold = kwargs.get('burst_threshold', 0.5)
        self.min_burst_length = kwargs.get('min_burst_length', 1)
        self.run_threshold = kwargs.get('run_threshold', 10)
        self.min_run_length = kwargs.get('min_run_length', 1)
        self.binsize = kwargs.get('binsize', 60)
        self.hist_density = kwargs.get('hist_density', False)
        self.ignorelongilis = kwargs.get('ignorelongilis', False)
        self.remove_longlicks = kwargs.get('remove_longlicks', False)
        self.only_return_first_n_bursts = kwargs.get('only_return_first_n_bursts', False)
        
        ## Read in and process data
        self.licks_raw = np.array(kwargs.get('licks', None))  # Store original licks
        self.licks = self.licks_raw.copy()

        if "offset" in kwargs:
            self.offset_raw = np.array(kwargs['offset'])  # Store original offsets
            self.offset = self.offset_raw.copy()
            
            # Calculate lick lengths first (before any filtering)
            temp_licklength = self.get_licklengths()
            
            if len(temp_licklength) > 0:
                # Identify longlicks before filtering
                temp_longlicks = temp_licklength[temp_licklength > self.longlick_threshold]
                self.longlicks = temp_longlicks if len(temp_longlicks) > 0 else None
                
                # Remove longlicks if requested
                if self.remove_longlicks and self.longlicks is not None:
                    # Create mask to keep only non-longlicks
                    keep_mask = temp_licklength <= self.longlick_threshold
                    n_to_keep = min(len(self.licks), len(keep_mask))
                    self.licks = self.licks[:n_to_keep][keep_mask[:n_to_keep]]
                    self.offset = self.offset[:n_to_keep][keep_mask[:n_to_keep]]
                
                # Calculate final licklength on filtered data
                self.licklength = self.get_licklengths()
                self.licklength_mode = get_mode(self.licklength)
            else:
                self.longlicks = None
                self.licklength = temp_licklength
                self.licklength_mode = None
        else:
            self.offset_raw = None
            self.offset = None
            self.licklength = None
            self.longlicks = None
        
        self.ilis = self.get_ilis()
        self.total = self.get_total_licks()

        self.burst_inds = self.get_burst_inds()
        self.burst_licks = self.get_burst_licks()
        self.burst_start = self.get_burst_start()
        self.burst_end = self.get_burst_end()
        self.burst_lengths = self.get_burst_lengths()

        if self.min_burst_length > 1:
            self.remove_short_bursts()
        
        # Keep only first N bursts if requested
        if self.only_return_first_n_bursts and isinstance(self.only_return_first_n_bursts, int):
            self.keep_first_n_bursts(self.only_return_first_n_bursts)

        self.burst_number = self.get_burst_number()
        self.burst_mean = self.get_burst_mean()
        self.burst_mean_first3 = self.get_burst_mean(number=3)
        self.intraburst_freq = self.get_intraburst_freq()
        self.intraburst_mode = self.get_intraburst_mode()
        self.interburst_intervals = self.get_interburstintervals()
        
        # then lick runs
        self.runs = self.get_runs()
        self.runs_start = self.get_run_start()
        self.runs_inds = self.get_run_inds()
        self.runs_end = self.get_run_end()
        self.runs_licks = self.get_run_licks()
        self.runs_length = self.get_run_lengths()
        if self.min_run_length > 1:
            self.remove_short_runs()
        self.runs_number = len(self.runs)
            
        # then burst probability
        self.burst_prob = self.get_burst_probability()
        self.weibull_params = self.get_weibull_params()

        self.histogram = self.get_histogram()

    def get_licklengths(self):
        onsets = self.licks[:len(self.offset)]
        return self.offset - onsets

    def get_longlicks(self):
        if np.min(self.licklength) < 0:
            print("One or more offsets precede onsets. Not doing lick length analysis.")
            return None
        else:
            return self.licklength[self.licklength > self.longlick_threshold]

    def get_ilis(self):
        ilis = np.diff(self.licks)
        if self.ignorelongilis:
            return ilis[ilis < self.burst_threshold]
        else:
            return ilis
        
    def get_ilis_in_bursts(self):
        tmp_burst = []
        all_rows = []
        burst_idx = 0
        for idx, ili in enumerate(np.diff(self.licks)):
            if ili < self.burst_threshold:
                tmp_burst.append(ili)
            else:
                df_temp = pd.DataFrame({"burst_index": burst_idx,
                                        "ili_index": np.arange(len(tmp_burst)),
                        "ili": tmp_burst,
                        "pre_ili": np.diff(self.licks)[idx-1-len(tmp_burst)],
                        "post_ili": ili
                        })
                all_rows.append(df_temp)
                burst_idx += 1
                tmp_burst = []

        self.ilis_in_bursts = pd.concat(all_rows, ignore_index=True)
        
        return self.ilis_in_bursts
    
    def get_first_n_ilis_in_bursts(self, n_ilis=5, pre_ili=4, min_ili=0.06):

        burst_df = self.get_ilis_in_bursts()
        
        return (burst_df
                .query("pre_ili > @pre_ili")
                .query("ili > @min_ili")
                .groupby("ili_index")
                .mean()
                .query("ili_index < @n_ilis")
                .ili
                )

    def get_total_licks(self):
        return len(self.licks)

    def get_burst_inds(self):
        burst_inds = (np.where(np.diff(self.licks) > self.burst_threshold)[0] + 1).tolist()
        burst_inds = [0] + burst_inds
        return burst_inds
    
    def get_burst_licks(self):
        return np.diff(self.burst_inds + [self.total]).tolist()
    
    def get_burst_start(self):
        return self.licks[self.burst_inds].tolist()
    
    def get_burst_end(self):
        end = self.licks[np.array(self.burst_inds[1:], dtype=int) - 1]
        return end.tolist() + [self.licks[-1]]
    
    def get_burst_lengths(self):
        return [x - y for x, y in zip(self.burst_end, self.burst_start)]
    
    def remove_short_bursts(self):
        inds_to_keep = [i for i, val in enumerate(self.burst_licks) if val >= self.min_burst_length]
        for burst_var in ['burst_inds', 'burst_licks', 'burst_start', 'burst_end', 'burst_lengths']:
            setattr(self, burst_var, [getattr(self, burst_var)[i] for i in inds_to_keep])
    
    def keep_first_n_bursts(self, n):
        """Keep only the first N bursts. If fewer than N bursts exist, keeps all."""
        if n <= 0:
            return  # Do nothing if n is 0 or negative
        
        # Determine how many bursts to keep (min of n or total bursts)
        n_to_keep = min(n, len(self.burst_inds))
        
        # Slice all burst-related lists to keep only first n bursts
        for burst_var in ['burst_inds', 'burst_licks', 'burst_start', 'burst_end', 'burst_lengths']:
            current_list = getattr(self, burst_var)
            setattr(self, burst_var, current_list[:n_to_keep])

    def get_burst_number(self):
        return len(self.burst_inds)
    
    def get_burst_mean(self, number=None):
        if self.burst_number == 0:
            return None
        if number is None:
            return np.mean(self.burst_licks)
        elif number < self.burst_number:
            return np.mean(self.burst_licks[:number])
        else:
            return np.mean(self.burst_licks)

    def get_intraburst_freq(self):
        if self.burst_number == 0 or np.max(self.burst_licks) < 2:
            return None
        else:
            return 1/np.mean([x for x in self.get_ilis() if x < self.burst_threshold])
        
    def get_intraburst_mode(self):
        if self.burst_number == 0 or np.max(self.burst_licks) < 2:
            return None
        else:
            return get_mode([x for x in self.get_ilis() if x < self.burst_threshold])

    def get_interburstintervals(self):
        if self.burst_number == 0:
            return None
        else:
            return np.array(self.burst_start[1:]) - np.array(self.burst_end[:-1])
    
    def get_runs(self):
        split_points = np.where(np.array(np.diff(self.licks)) > self.run_threshold)[0] + 1
        return np.split(self.licks, split_points)
    
    def get_run_start(self):
        return [run[0] for run in self.runs]
    
    def get_run_inds(self):
        return np.where(np.isin(self.licks, self.runs_start))[0].tolist()
    
    def get_run_end(self):
        return [run[-1] for run in self.runs]
    
    def get_run_licks(self):
        return [len(run) for run in self.runs]
    
    def get_run_lengths(self):
        return [run[-1] - run[0] for run in self.runs]
    
    def remove_short_runs(self):
        inds_to_keep = [i for i, val in enumerate(self.runs_licks) if val >= self.min_run_length]
        for run_var in ['runs', 'runs_start', 'runs_inds', 'runs_end', 'runs_licks', 'runs_length']:
            setattr(self, run_var, [getattr(self, run_var)[i] for i in inds_to_keep])

    def get_burst_probability(self):
        if self.burst_number == 0:
            return None
        else:
            return calculate_burst_prob(self.burst_licks)
    
    def get_weibull_params(self):
        if self.burst_number == 0:
            return None
        else:
            try:
                return fit_weibull(self.burst_prob[0], self.burst_prob[1])
            except:
                return None
    
    def get_histogram(self):
        bins = np.arange(0, len(self.licks), self.binsize)
        return np.histogram(self.licks, bins=bins, density=self.hist_density)[0]
    
def calculate_burst_prob(bursts):
    """
    Calculates cumulative burst probability as in seminal Davis paper
    DOI: 10.1152/ajpregu.1996.270.4.R793

    Parameters
    ----------
    bursts : List
        List with lengths of bursts.

    Returns
    -------
    x : List
        x values (bin sizes).
    y : List
        y values of cumulative burst probability.

    """
    bins = np.arange(min(bursts), max(bursts))
    hist=np.histogram(bursts, bins=bins, density=True)
    cumsum=np.cumsum(hist[0])

    x = hist[1][1:]
    y = [1-val for val in cumsum]
    
    return x, y

def weib_davis(x, alpha, beta):
    '''Weibull function as used in Davis (1998) DOI: 10.1152/ajpregu.1996.270.4.R793'''
    try:
        # Ensure inputs are arrays for vectorized operations
        x = np.asarray(x)
        
        # Handle edge cases
        if alpha <= 0 or beta <= 0:
            return np.full_like(x, np.nan, dtype=float)
        
        # Calculate the exponent, handling potential overflow
        exponent = -(alpha * x)**beta
        
        # Clip very large negative exponents to prevent underflow to 0
        # exp(-700) is approximately the smallest representable positive float
        exponent = np.clip(exponent, -700, 0)
        
        return np.exp(exponent)
        
    except (ValueError, OverflowError, ZeroDivisionError):
        # Return NaN for invalid inputs
        return np.full_like(np.asarray(x), np.nan, dtype=float)

def fit_weibull(xdata, ydata):
    '''Fits Weibull function to xdata and ydata and returns fit parameters.'''
    x0=np.array([0.1, 1])
    fit=opt.curve_fit(weib_davis, xdata, ydata, x0)
    alpha=fit[0][0]
    beta=fit[0][1]
    slope, intercept, r_value, p_value, std_err = stats.linregress(ydata, weib_davis(xdata, alpha, beta))
    r_squared=r_value**2
    
    return alpha, beta, r_squared

def get_mode(data, binsize=0.001, smooth_window=20):
    hist = np.histogram(data, bins=np.arange(0, np.max(data) + binsize, binsize))
    hist_smoothed = pd.Series(hist[0]).rolling(smooth_window, center=True).mean()
    return hist_smoothed.idxmax() * binsize

    # need to test with different files and times when zero licks are given etc
        # and when licks are gtiven but no bursts


# idea to add for some of these calculator functions optional arguments that allow one to specify subsets of data
# to make it easier to for example do calculations of each quarter of a session - by licks, or by time
# or to do calculations for different types of licks (e.g. licks during reward vs licks during non-reward)



    # lickdata = Lickcalc(licks="hello")
