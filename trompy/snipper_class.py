import numpy as np
from math import ceil, floor

class Snipper:
    def __init__(self, data, start, **kwargs):
        self.data = data
        self.start = [i for i in start if np.isfinite(i)]
        self.kwargs = kwargs

        if 'end' in kwargs:
            self.end = [i for i in kwargs['end'] if np.isfinite(i)]
        else:
            self.end = None

        if 'fs' in kwargs:
            self.fs = kwargs['fs']

        if 'pre' in kwargs:
            self.pre = kwargs['pre']
        else:
            self.pre = 10

        if 'post' in kwargs:
            self.post = kwargs['post']
        else:
            self.post = 10

        if 'binlength' in kwargs:
            self.binlength = kwargs['binlength']
        else:
            self.binlength = None

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


        # adjust baseline
        if self.binlength:
            self.bin_snips()
            return self.binned_snips

        return self.snips
    
    def longsnipper(self):
        self.nsnips = len(self.events_in_samples)
        self.snips = []
        for start, stop in zip(self.events_in_samples, self.event_end_in_samples):
            self.snips.append(self.data[start - int(self.pre * self.fs) : stop + int(self.post * self.fs)])\

    def adjust_baseline(self):
        pass

    def put_snip_in_bins(self, snip):
        bins = int(len(snip)/(self.fs * self.binlength))
        remainder_samples = len(snip) % bins
        if remainder_samples == 0:
            return np.reshape(snip, (bins, -1)).mean(axis=1)
        else:
            return np.reshape(snip[:-remainder_samples], (bins, -1)).mean(axis=1)
    
    def bin_snips(self):
        self.binned_snips = [self.put_snip_in_bins(snip) for snip in self.snips]


    
        
if __name__ == '__main__':
    data = np.random.rand(100000)
    start = [20, 75]
    end = [30, 80]
    snipper = Snipper(data, start, end=end, fs=1017, pre=10, post=10, binlength=0.1)
    snips = snipper.get_snips()
    print(snips)  
    for snip in snips:
        print(len(snip))

    snipper.binlength = 0.2
    snips = snipper.get_snips()
    print(snips)  
    for snip in snips:
        print(len(snip))
