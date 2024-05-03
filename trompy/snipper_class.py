from pathlib import Path
import numpy as np
from math import ceil, floor
import pickle
import matplotlib.pyplot as plt
from trompy.lick_utils import lickCalc
from trompy.snipper_utils import findnoise, makerandomevents

class Snipper:
    def __init__(self, data, start, **kwargs):
        self.data = data
        self.start = [i for i in start if np.isfinite(i)]
        self.kwargs = kwargs

        self.end = kwargs.get('end', None)
        self.fs = kwargs.get('fs', 1)
        self.pre = kwargs.get('pre', 10)
        self.post = kwargs.get('post', 20)
        self.baselinelength = kwargs.get('baselinelength', self.pre)
        self.adjustbaseline = kwargs.get('adjustbaseline', True)
        self.binlength = kwargs.get('binlength', None)
        self.zscore = kwargs.get('zscore', False)
        self.truncate = kwargs.get('truncate', False)
        self.mineventlength = kwargs.get('mineventlength', 0)
        self.remove_artifacts = kwargs.get('remove_artifacts', False)

    # should I return snips directly when making the class or wait for the user to call a method?

    def get_snips(self):
        
        self.events_in_samples = [int(timestamp*self.fs) for timestamp in self.start]

        if self.end:
            self.event_end_in_samples = [int(timestamp*self.fs) for timestamp in self.end]
            self.longsnipper()
        else:
            self.trial_length_in_samples = int((self.pre + self.post) * self.fs)

            # removes events where an entire snip cannot be made
            self.events_in_samples = [event for event in self.events_in_samples if \
                (event - (self.pre * self.fs) > 0) and \
                (event + (self.post * self.fs) < len(self.data))]

            self.nsnips = len(self.events_in_samples)
            self.snips = np.empty([self.nsnips, self.trial_length_in_samples])
        
            self.trial_start = [event - ceil(self.pre * self.fs) for event in self.events_in_samples]
            self.trial_end = [event + ceil(self.post * self.fs) for event in self.events_in_samples]

            for idx, timestamp in enumerate(self.trial_start):
                self.snips[idx] = self.data[timestamp : timestamp + self.trial_length_in_samples]

        if self.truncate:
            self.truncate_to_same_length()

        if self.remove_artifacts:
            self.remove_artifacts_from_snips()
            
        self.set_baseline()
        if self.adjustbaseline:
            self.adjust_baseline()

        if self.binlength:
            self.bin_snips()
            self.binned = True
        else:
            self.binned = False

        if self.zscore:
            self.zscore_snips()

        return self.snips
    
    def longsnipper(self):
        self.nsnips = len(self.events_in_samples)
        self.snips = []
        for start, stop in zip(self.events_in_samples, self.event_end_in_samples):
            self.snips.append(self.data[start - int(self.pre * self.fs) : stop + int(self.post * self.fs)])
            
    def truncate_to_same_length(self):
        self.bins_per_trial = int((self.mineventlength + self.pre + self.post) / self.binlength)
        self.truncated_array = np.empty([len(self.snips), self.bins_per_trial])
        self.bins_per_section = int(self.bins_per_trial/2)
        
        for idx, snip in enumerate(self.snips):
            self.truncated_array[idx,:self.bins_per_section] = snip[:self.bins_per_section]
            self.truncated_array[idx,-self.bins_per_section] = snip[-self.bins_per_section]

        self.snips = self.truncated_array

    def remove_artifacts_from_snips(self):
        self.artifact_threshold = 10
        bgMAD = findnoise(self.data, makerandomevents(120, int(len(self.data)/self.fs)-120),
                              fs=self.fs, 
                              method='sum')

        sigSum = [np.sum(abs(i)) for i in self.snips]
        self.noiseindex = [i > bgMAD * self.artifact_threshold for i in sigSum]
        self.snips = [self.snips[i] for i in range(len(self.snips)) if not self.noiseindex[i]]

    def set_baseline(self):
        try:
            if len(self.baselinelength) == 2:
                self.baseline_start_in_samples = int(self.baselinelength[0] * self.fs)
                self.baseline_end_in_samples = int((self.baselinelength[0] - self.baselinelength[1]) * self.fs)
            else:
                print("Incorrect number of values given for baselinelength. Using first value only.")
                self.baseline_start_in_samples = int(self.baselinelength[0] * self.fs)
                self.baseline_end_in_samples = int(self.baselinelength[0] * self.fs)
        except TypeError:
            self.baseline_start_in_samples = int(self.baselinelength * self.fs)
            self.baseline_end_in_samples = int(self.baselinelength * self.fs)
    
    def adjust_baseline(self):
        # doesn't currently use baseline start, only calculates baseline from beginning of snip to baseline end
        if type(self.snips) == list:
            adj_snips = []
            for snip in self.snips:
                baseline = np.mean(snip[: self.baseline_end_in_samples])
                adj_snips.append(np.subtract(snip, baseline))
            self.snips = adj_snips
        else:
            average_baseline = np.mean(self.snips[:, : self.baseline_end_in_samples], axis=1)
            self.snips = np.subtract(self.snips.transpose(), average_baseline).transpose()

    def put_snip_in_bins(self, snip):
        bins = ceil(len(snip)/(self.fs * self.binlength))
        remainder_samples = len(snip) % bins
        if remainder_samples == 0:
            return np.reshape(snip, (bins, -1)).mean(axis=1)
        else:
            return np.reshape(snip[:-remainder_samples], (bins, -1)).mean(axis=1)
    
    def bin_snips(self):
        self.snips = np.array([self.put_snip_in_bins(snip) for snip in self.snips])

    def zscore_snips(self):
        if self.binned:
            baselinelength_for_zscore = int(self.baseline_end_in_samples / self.fs / self.binlength)
        else:
            baselinelength_for_zscore = self.baseline_end_in_samples
            
        z_snips = []
        for snip in self.snips:
            mean = np.mean(snip[: baselinelength_for_zscore])
            sd = np.std(snip[: baselinelength_for_zscore])
            z_snips.append([(x - mean) / sd for x in snip])
        try:
            self.snips = np.array(z_snips)
        except:
            pass

    def plot(self, ax=None, **kwargs):

        if ax == None:
            f, ax = plt.subplots(1, 1)
            
        color = kwargs.get('color', "black")
        alpha = kwargs.get('alpha', 0.3)
        mean_color = kwargs.get('mean_color', 'red')
                
        for snip in self.snips:
            ax.plot(snip, color=color, alpha=alpha)
            
        ax.plot(np.mean(self.snips, axis=0), color=mean_color, linewidth=2)
        
        return f, ax
        
    def plot_shaded_error(self, ax=None, **kwargs):
        if not self.check_snips_array():
            print("Is there an issue with the snips array?")
            return
        
        if ax == None:
            f, ax = plt.subplots(1, 1)
            
        color = kwargs.get('color', "orange")
        error = kwargs.get('error', "sem")
            
        mean = np.mean(self.snips, axis=0)
        if error == "sem":
            error_values = np.std(self.snips, axis=0) / np.sqrt(len(self.snips))
        else:
            error_values = np.std(self.snips, axis=0)
            
        ax.plot(mean, color=color)
        ax.fill_between(range(len(mean)), mean-error_values, mean+error_values, color=color, alpha=0.3)
        
        return f, ax

    def plot_heatmap(self):
        # can use existence of self.bins_per_section
        pass
    
    def check_snips_array(self):
        print(type(self.snips))
        if isinstance(self.snips, np.ndarray):
            return True
        else:
            try:
                self.snips = np.array(self.snips)
                return True
            except:
                self.truncate_to_same_length()
                return
            
    def check_for_ragged_array(self):
        # add little code to check whether self.snips is a 2D matrix
        # pass

if __name__ == '__main__':
    # data = np.random.rand(100000)
    # start = [20, 75]
    # end = [30, 80]
    # snipper = Snipper(data, start, end=end, fs=1017, pre=10, post=10, binlength=0.1, adjustbaseline=False, baselinelength=[10, 5])
    # snips = snipper.get_snips()
    # print(snips)  
    # print(snipper.binlength)
    # for snip in snips:
    #     print(len(snip))

    # snipper.binlength = 0.2
    # snips = snipper.get_snips()
    # print(snips)  
    # for snip in snips:
    #     print(len(snip))

    DATAPATH = Path("C:/Users/jmc010/Data/histamine/restricted_dark_full_data.pickle")
    DATAPATH = Path("D:/TestData/photometry/histamine/restricted_dark_full_data.pickle")

    with open(DATAPATH, 'rb') as handle:
        restricted_dark = pickle.load(handle)
    
    d = restricted_dark["HL208_6"]
    lickdata = lickCalc(d["licks"], minrunlength=3)
    data = d["corrected"]
    fs = d["fs"]
    start = lickdata["rStart"]

    snipper = Snipper(data, start, fs=fs, binlength=0.1, remove_artifacts=True, adjustbaseline=True, baselinelength=[10, 5])
    s = snipper.get_snips()