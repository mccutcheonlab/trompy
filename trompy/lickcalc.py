
from pathlib import Path
import numpy as np
from scipy import stats
import scipy.optimize as opt

class Lickcalc:
    def __init__(self, **kwargs):
        ## Set default parameters

        if "longlick_threshold" in kwargs:
            self.longlick_threshold = kwargs['longlick_threshold']
        else:
            self.longlick_threshold = 0.3

        if "burst_threshold" in kwargs:
            self.burst_threshold = kwargs['burst_threshold']
        else:
            self.burst_threshold = 0.5

        if "min_burst_length" in kwargs:
            self.min_burst_length = kwargs['min_burst_length']
        else:
            self.min_burst_length = 1

        if "run_threshold" in kwargs:
            self.run_threshold = kwargs['run_threshold']
        else:
            self.run_threshold = 10

        if "min_run_length" in kwargs:
            self.min_run_length = kwargs['min_run_length']
        else:
            self.min_run_length = 1

        if "binsize" in kwargs:
            self.binsize = kwargs['binsize']
        else:
            self.binsize = 60

        if "hist_density" in kwargs:
            self.hist_density = kwargs['hist_density']
        else:
            self.hist_density = False     

        self.ignorelongilis = kwargs.get('ignorelongilis', False)
        
        ## Read in and process data
        self.licks = np.array(kwargs.get('licks', None))

        if "offset" in kwargs:
            self.offset = np.array(kwargs['offset'])
            self.licklength = self.get_licklengths()
            if len(self.licklength) > 0:
                self.longlicks = self.get_longlicks()
            else:
                self.longlicks = None
        else:
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

        self.burst_number = self.get_burst_number()
        self.burst_mean = self.get_burst_mean()
        self.burst_mean_first3 = self.get_burst_mean(number=3)
        self.intraburst_freq = self.get_intraburst_freq()
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
        if min(self.licklength) < 0:
            print("One or more offsets precede onsets. Not doing lick length analysis.")
            return None
        else:
            return [x for x in self.licklength if x > self.longlick_threshold]

    def get_ilis(self):
        if self.ignorelongilis:
            return [x for x in np.diff(self.licks) if x < self.burst_threshold]
        else:
            return np.diff(self.licks)

    def get_total_licks(self):
        return len(self.licks)

    def get_burst_inds(self):
        burst_inds = (np.where(np.diff(self.licks) > self.burst_threshold)[0] + 1).tolist()
        if burst_inds[0] != 0:
            burst_inds = [0] + burst_inds
        return burst_inds
    
    def get_burst_licks(self):
        return [int(x) for x in np.diff(self.burst_inds + [self.get_total_licks()])]
    
    def get_burst_start(self):
        return self.licks[self.burst_inds].tolist()
    
    def get_burst_end(self):
        end = self.licks[np.array(self.burst_inds[1:]) - 1]
        return end.tolist() + [self.licks[-1]]
    
    def get_burst_lengths(self):
        return [x - y for x, y in zip(self.burst_end, self.burst_start)]
    
    def remove_short_bursts(self):
        inds_to_keep = [i for i, val in enumerate(self.burst_licks) if val >= self.min_burst_length]
        for burst_var in ['burst_inds', 'burst_licks', 'burst_start', 'burst_end', 'burst_lengths']:
            setattr(self, burst_var, [getattr(self, burst_var)[i] for i in inds_to_keep])

    def get_burst_number(self):
        return len(self.burst_inds)
    
    def get_burst_mean(self, number=None):
        if self.burst_number == 0:
            return None
        if number == None:
            return np.mean(self.burst_licks)
        elif number < self.burst_number:
            return np.mean(self.burst_licks[number])
        else:
            return np.mean(self.burst_licks)

    def get_intraburst_freq(self):
        if self.burst_number == 0 or np.max(self.burst_licks) < 2:
            return None
        else:
            return 1/np.mean([x for x in self.get_ilis() if x < self.burst_threshold])

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
    return (np.exp(-(alpha*x)**beta))

def fit_weibull(xdata, ydata):
    '''Fits Weibull function to xdata and ydata and returns fit parameters.'''
    x0=np.array([0.1, 1])
    fit=opt.curve_fit(weib_davis, xdata, ydata, x0)
    alpha=fit[0][0]
    beta=fit[0][1]
    slope, intercept, r_value, p_value, std_err = stats.linregress(ydata, weib_davis(xdata, alpha, beta))
    r_squared=r_value**2
    
    return alpha, beta, r_squared

    # need to test with different files and times when zero licks are given etc
        # and when licks are gtiven but no bursts


# idea to add for some of these calculator functions optional arguments that allow one to specify subsets of data
# to make it easier to for example do calculations of each quarter of a session - by licks, or by time
# or to do calculations for different types of licks (e.g. licks during reward vs licks during non-reward)


if __name__ == '__main__':
    print('Testing functions')
    import trompy as tp
    filename = Path("C:/Users/jmc010/Github/trompy/tests/test_data/03_W.med")

    data = tp.medfilereader(filename, vars_to_extract=["e", "f"], remove_var_header=True)

    lickdata = Lickcalc(licks=data[0], offset=data[1], min_burst_length=3)

    # print(dir(lickdata))


    lickdata = Lickcalc(licks=[2.3,5.6,10.2])


    # lickdata = Lickcalc(licks="hello")
