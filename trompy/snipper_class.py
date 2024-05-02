import numpy as np
from math import ceil, floor
import matplotlib.pyplot as plt

class Snipper:
    def __init__(self, data, start, **kwargs):
        self.data = data
        self.start = [i for i in start if np.isfinite(i)]
        self.kwargs = kwargs

        self.end = kwargs.get('end', None)
        self.fs = kwargs.get('fs', 1)
        self.pre = kwargs.get('pre', 10)
        self.post = kwargs.get('post', 10)
        self.baselinelength = kwargs.get('baselinelength', self.pre)
        self.adjustbaseline = kwargs.get('adjustbaseline', True)
        self.binlength = kwargs.get('binlength', None)
        self.zscore = kwargs.get('zscore', False)
        self.truncate = kwargs.get('truncate', False)

    # should I return snips directly when making the class or wait for the user to call a method?

    def get_snips(self):
        
        self.events_in_samples = [ceil(timestamp*self.fs) for timestamp in self.start]

        if self.end:
            self.event_end_in_samples = [ceil(timestamp*self.fs) for timestamp in self.end]
            self.longsnipper()
        else:
            self.trial_length_in_samples = int((self.pre + self.post) * self.fs)

            # removes events where an entire snip cannot be made
            self.events_in_samples = [event for event in self.events_in_samples if \
                (event - (self.pre * self.fs) > 0) and \
                (event + (self.post * self.fs) < len(self.data))]

            self.nsnips = len(self.events_in_samples)
            self.snips = np.empty([self.nsnips, self.trial_length_in_samples])
        
            self.trial_start = [event - int(self.pre * self.fs) for event in self.events_in_samples]
            self.trial_end = [event + int(self.post * self.fs) for event in self.events_in_samples]

            for idx, (start, end) in enumerate(zip(self.trial_start, self.trial_end)):
                self.snips[idx] = self.data[start : end]

        if self.truncate:
            self.truncate_to_same_length()

        if self.adjustbaseline:
            self.set_baseline()
            self.adjust_baseline()

        if self.binlength:
            self.bin_snips()

        if self.zscore:
            self.zscore_snips()

        return self.snips
    
    def longsnipper(self):
        self.nsnips = len(self.events_in_samples)
        self.snips = []
        for start, stop in zip(self.events_in_samples, self.event_end_in_samples):
            self.snips.append(self.data[start - int(self.pre * self.fs) : stop + int(self.post * self.fs)])\

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
        bins = int(len(snip)/(self.fs * self.binlength))
        remainder_samples = len(snip) % bins
        if remainder_samples == 0:
            return np.reshape(snip, (bins, -1)).mean(axis=1)
        else:
            return np.reshape(snip[:-remainder_samples], (bins, -1)).mean(axis=1)
    
    def bin_snips(self):
        self.snips = [self.put_snip_in_bins(snip) for snip in self.snips]

    def zscore_snips(self):
        self.snips = (self.snips - np.mean(self.snips, axis=1)[:, np.newaxis]) / np.std(self.snips, axis=1)[:, np.newaxis]

    def remove_artifacts(self):
        pass

    def truncate_to_same_length(self):
        pass

    def plot(self, ax=None, **kwargs):
        if ax == None:
            f, ax = plt.subplots(1, 1)

        

    def plot_heatmap(self):
        pass
    
        
if __name__ == '__main__':
    data = np.random.rand(100000)
    start = [20, 75]
    end = [30, 80]
    snipper = Snipper(data, start, end=end, fs=1017, pre=10, post=10, binlength=0.1, adjustbaseline=False, baselinelength=[10, 5])
    snips = snipper.get_snips()
    print(snips)  
    print(snipper.binlength)
    for snip in snips:
        print(len(snip))

    snipper.binlength = 0.2
    snips = snipper.get_snips()
    print(snips)  
    for snip in snips:
        print(len(snip))

    snipper.plot()
