# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:22:07 2020

@author: admin
"""

# Import statements
import warnings
import matplotlib as mpl
try:
    mpl.use("TkAgg")
except:
    warnings.warn("Unable to set TKAgg as matplotlib backend for GUI", ImportWarning)
    
import sys
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import subprocess
import string
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import StrMethodFormatter
import ntpath
import csv
import collections
import tdt
import xlsxwriter as xl
from pathlib import Path

import pandas as pd

from scipy.signal import medfilt, butter, filtfilt
from scipy.stats import linregress
from scipy.optimize import curve_fit, minimize

import io
from contextlib import redirect_stdout

from trompy import *

# Main class for GUI
class Window_photo(Frame):
    
    def __init__(self, master=None, quickstart=False):

        f1 = ttk.Style()
        f1.configure('.', background='powder blue', padding=5)
        f1.configure('TButton', width=15, sticky=(E,W))
        f1.configure('TEntry', width=7)
        f2 = ttk.Style()
        f2.configure('inner.TFrame', background='light cyan')

        ttk.Frame.__init__(self, master, style='TFrame', padding=(10, 10, 15, 15))

        self.master = master
        self.quickstart = quickstart     
        self.startdir = Path(os.getcwd())
        self.init_window()
        
        self.master.bind_all("<Return>", self.callback)
        self.master.bind_all("n", self.callback2)

    def init_window(self):
    
        self.master.title('Photometry Analyzer')
        self.pack(fill=BOTH, expand=1)

        #Frames for session window and snipits
        self.f2 = ttk.Frame(self, style='inner.TFrame', relief='sunken',
                            borderwidth=5, height=150)        
        self.f3 = ttk.Frame(self, style='inner.TFrame', relief='sunken',
                            borderwidth=5, height=150)
        self.f4 = ttk.Frame(self, style='inner.TFrame', relief='sunken',
                            borderwidth=5, height=200, width=200)
        self.f5 = ttk.Frame(self, style='inner.TFrame', relief='sunken',
                            borderwidth=5, height=200, width=200)
        self.f6 = ttk.Frame(self, style='inner.TFrame', relief='sunken',
                            borderwidth=5, height=200, width=200)

        self.terminal = Text(self, bg='black', fg='white')
        self.terminal.insert(INSERT, "Photometry Analyzer 3.0")
        self.terminal.grid(column=0, row=16, columnspan=10, sticky=(N,S,E,W))

        # Button definitions
        self.choosefileBtn = ttk.Button(self, text='Choose files', command=self.choosefile)
        # self.loaddataBtn = ttk.Button(self, text='Load data', command=self.loaddata)
        self.makelickrunsBtn = ttk.Button(self, text='Lick runs', command=self.makelickruns)
        self.makesnipsBtn = ttk.Button(self, text='Make Snips', command=self.refresh)
        self.noiseBtn = ttk.Button(self, text='Toggle noise', command=self.togglenoise)
        self.prevtrialBtn = ttk.Button(self, text='Prev Trial', command=self.prevtrial)
        self.nexttrialBtn = ttk.Button(self, text='Next Trial', command=self.nexttrial)
        self.showallBtn = ttk.Button(self, text='Show All', command=self.showall)
        self.refreshBtn = ttk.Button(self, text='Refresh', command=self.refresh)
        self.defaultfolderBtn = ttk.Button(self, text='Default folder', command=self.chooseexportfolder)
        self.makeexcelBtn = ttk.Button(self, text='Make Excel', command=self.makeExcel)
        self.savefigsBtn = ttk.Button(self, text='Save Figs', command=self.savefigs)
        self.toggletipsBtn = ttk.Button(self, text='Toggle tips', command=self.toggletips)

        # Label definitions
        self.shortfilename = StringVar(self.master)
        self.shortfilename.set('No tank chosen')
        self.filenameLbl = ttk.Label(self, textvariable=self.shortfilename, wraplength=200)
        self.timelockLbl = ttk.Label(self, text='--Timelocked event--')
        self.timelockoptionsLbl = ttk.Label(self, text='--Trial options--')
        
        # self.primarysigLbl = ttk.Label(self, text='Primary signal')
        # self.autofsigLbl = ttk.Label(self, text='AutoFl. signal')
        
        self.baselineLbl = ttk.Label(self, text='Baseline (s)')
        self.lengthLbl = ttk.Label(self, text='Snip length (s)')
        self.fsnipLbl = ttk.Label(self, text='Snip freq (Hz)')
        self.noisethLbl = ttk.Label(self, text='Noise threshold')
        
        self.suffixLbl = ttk.Label(self, text='File suffix')
        
        # Field and entries
        self.baseline = StringVar(self.master)
        self.baselineField = ttk.Entry(self, textvariable=self.baseline)
        self.baselineField.insert(END, '10')

        self.length = StringVar(self.master)
        self.lengthField = ttk.Entry(self, textvariable=self.length)
        self.lengthField.insert(END, '30')
        
        self.fsnip = StringVar(self.master)
        self.fsnipField = ttk.Entry(self, textvariable=self.fsnip)
        self.fsnipField.insert(END, '10')
        
        self.noiseth = StringVar(self.master)
        self.noisethField = ttk.Entry(self, textvariable=self.noiseth)
        self.noisethField.insert(END, '10')
        
        self.currenttrial = StringVar(self.master)
        self.currenttrialField = ttk.Entry(self, textvariable=self.currenttrial)
        self.currenttrialField.insert(END, '')
        
        self.suffix = StringVar(self.master)
        self.suffixField = ttk.Entry(self, textvariable=self.suffix)

        # Progress bar and about label
        self.progress = ttk.Progressbar(self, orient=HORIZONTAL, length=200, mode='determinate')

        self.aboutLbl = ttk.Label(self, text='Photometry Analyzer-3.0 by J McCutcheon')

        # Packing grid with widgets
        self.f2.grid(column=2, row=0, columnspan=3, rowspan=5, sticky=(N,S,E,W))
        self.f3.grid(column=5, row=0, columnspan=3, rowspan=5, sticky=(N,S,E,W))
        self.f4.grid(column=2, row=7, columnspan=2, rowspan=5, sticky=(N,S,E,W))
        self.f5.grid(column=4, row=7, columnspan=2, rowspan=5, sticky=(N,S,E,W))
        self.f6.grid(column=6, row=7, columnspan=2, rowspan=5, sticky=(N,S,E,W))
        
        # for frame in [self.f2, self.f3, self.f4, self.f5, self.f6]:
        #     frame.columnconfigure(0, weight=1)
        #     frame.rowconfigure(0, weight=1)

        for row_index in range(17):
            Grid.rowconfigure(self, row_index, weight=1)
            for col_index in range(9):
                Grid.columnconfigure(self, col_index, weight=1)
        # Grid.rowconfigure(self, 16, weight=1)
                
        self.choosefileBtn.grid(column=0, row=0, rowspan=2, sticky=(N,S,E,W))
        # self.loaddataBtn.grid(column=0, row=2,rowspan=2, sticky=(N,S,E,W))
        self.filenameLbl.grid(column=0, row=4, rowspan=2, sticky=(E,W))
        self.timelockLbl.grid(column=0, row=4, rowspan=2, sticky=(E,W))
        self.timelockoptionsLbl.grid(column=1, row=4, rowspan=2, sticky=(E,W))
        
        self.toggletipsBtn.grid(column=9, row=0)
        
        # self.primarysigLbl.grid(column=1, row=0)
        # self.autofsigLbl.grid(column=1, row=2)
        
        self.baselineLbl.grid(column=0, row=8, sticky=E)
        self.baselineField.grid(column=1, row=8)
        self.lengthLbl.grid(column=0, row=9, sticky=E)
        self.lengthField.grid(column=1, row=9)
        self.fsnipLbl.grid(column=0, row=10, sticky=E)
        self.fsnipField.grid(column=1, row=10)
        self.noisethLbl.grid(column=0, row=11, sticky=E)
        self.noisethField.grid(column=1, row=11)
        
        self.prevtrialBtn.grid(column=2, row=12)
        self.nexttrialBtn.grid(column=2, row=13)
        self.currenttrialField.grid(column=3, row=12)
        self.showallBtn.grid(column=3, row=13, sticky=(W, E))
        
        self.refreshBtn.grid(column=7, row=12, sticky=(W, E))
        
        self.makesnipsBtn.grid(column=9, row=7, rowspan=2, sticky=(N, S, W,E))
        self.noiseBtn.grid(column=9, row=9, rowspan=2, sticky=(N, S, W,E))
        
        self.aboutLbl.grid(column=0, row=14, columnspan=3, sticky=W)
        self.progress.grid(column=0, row=15, columnspan=2, sticky=(W, E))
        
        self.suffixLbl.grid(column=2, row=15, sticky=E)
        self.suffixField.grid(column=3, row=15, sticky=(W, E))
        self.defaultfolderBtn.grid(column=4, row=15, sticky=(W, E))
        self.makeexcelBtn.grid(column=5, row=15, sticky=(W, E))
        self.savefigsBtn.grid(column=6, row=15, sticky=(W, E))
     
        self.blue = StringVar(self.master)       
        self.uv = StringVar(self.master)  
        self.eventsVar = StringVar(self.master)
        self.trialtypeVar = StringVar(self.master)
        
        self.trialselectVar = StringVar(self.master)
        self.lickrunsVar = StringVar(self.master)
        self.snipsVar = StringVar(self.master)
        self.noisethVar = IntVar(self.master)
        self.noise=True
        
        # self.updatesigoptions()
        self.updateeventoptions()
        
        self.sessionviewer()

        if self.quickstart:
            tips('Welcome to the photometry analyzer! First click "Choose tank" to select a tank to analyze')
        
    def callback(self, *args):

        if hasattr(self, 'data'):
            try:
                self.refresh()
            except: pass
    
    def callback2(self, *args):
        try:
            self.togglenoise()
        except: pass
        
    def refresh(self):
        self.makesnips()
    
    def choosefile(self):
        self.photofile = Path(filedialog.askopenfilename(initialdir=self.startdir, title='Select a data file.'))
        self.behavfile = Path(filedialog.askopenfilename(initialdir=self.startdir, title='Select a behavior file.'))
        
        self.startdir = self.photofile.parent
        self.shortfilename.set(ntpath.dirname(self.photofile))
        
        print(self.shortfilename.get())
        
        self.loaddata()
        
        # opens file to get stream and epoch names
        self.parsebehavfile()
        
        # update dropdown menu options
        self.updateeventoptions()
        
        if self.quickstart:
            tips('Great! Now select the correct values for your primary signal and autofluorescence signal. Then press "Load data"')

    def parsebehavfile(self):
        self.behavdf = pd.read_csv(self.behavfile)

        all_cols = list(self.behavdf.columns)
        self.epochfields = [col for col in all_cols if "time" in col]
        self.extrafields = [col for col in all_cols if col not in self.epochfields]

    def updateeventoptions(self):
        try:
            eventOptions = self.epochfields
            trialtypeOptions = self.extrafields

        except AttributeError:
            eventOptions = ['None']
            trialtypeOptions = ['None']

        
        self.chooseeventMenu = ttk.OptionMenu(self, self.eventsVar, eventOptions[0], *eventOptions)
        self.chooseeventMenu.grid(column=0, row=6)

        snipOptions = ['blue', 'uv', 'filt', 'filt_z']
        self.choosesnipMenu = ttk.OptionMenu(self, self.snipsVar, snipOptions[0], *snipOptions)
        self.choosesnipMenu.grid(column=6, row=12)
   
        self.trialtypeMenu = ttk.OptionMenu(self, self.trialtypeVar, trialtypeOptions[0], *trialtypeOptions, command=self.updatetrialselectoptions)
        self.trialtypeMenu.grid(column=1, row=6)
        
    def updatetrialselectoptions(self, event):       
        
        try:     
            trialselectOptions = ["All"] + list(self.behavdf[self.trialtypeVar.get()].unique())
        except:
            trialselectOptions = ['None']
                                
        self.trialselectMenu = ttk.OptionMenu(self, self.trialselectVar, trialselectOptions[0], *trialselectOptions)
        self.trialselectMenu.grid(column=1, row=7)

    def loaddata(self):
        
        # code to load in neurophotometrics data and perform filtering
        
        self.ts, self.ch1, self.ch2 = [], [], []

        with open(self.photofile, "r", newline='') as f:
            c = csv.reader(f, delimiter=',')
            for row in c:
                if row[2] == "6":
                    self.ts.append(float(row[1]))
                    self.ch1.append(float(row[3]))    
                elif row[2] == "1":
                    self.ch2.append(float(row[3]))
                else:
                    print("Not added:", row)
        
        self.data = self.ch1
        self.datauv = self.ch2
        self.t0 = self.ts[0]
        self.adj_ts = np.array(self.ts) - self.t0
        
        self.fs = 1/np.median(np.diff(self.ts))
        
        self.progress['value'] = 0
        
        self.addtoterminal("\nLoading streams...\n")
        
        
        # # process data
        self.datafilt = processdata_np(self.data, self.datauv, self.ts)
        # self.progress['value'] = 80
        
        # # set time vectors
        # self.t2sMap = time2samples(self.data, self.fs)
        # self.progress['value'] = 90
        
        # plot all session data
        self.sessionviewer()
        self.progress['value'] = 100
        
        if self.quickstart:
            tips('Super! Now you can pick a event to timelock your snips to - you can choose whether you want onset or offset, remove other events in the baseline, or even just make a series of random events. Once selected, click "Make snips"')
            self.number_of_times = 0
            
    def sessionviewer(self):
        try:
            self.makesessionfig(self.f2, self.data, self.datauv, 'F')
        except AttributeError:
            self.makesessionfig(self.f2, [], [], 'F')
            print("failed making figure")
            
        try:
            self.makesessionfig(self.f3, self.datafilt, [], 'Delta F')
        except AttributeError:
            self.makesessionfig(self.f3, [], [], 'Delta F')

    def makesessionfig(self, frame, data1, data2, ylabel):
        # parameters for polt bounding boxes
        bottom=0.23
        
        # plot blue and uv signals
        fig = Figure(figsize=(4,2))
        fig.subplotpars.bottom=bottom
        fig.subplotpars.left=0.2
        ax = fig.subplots(nrows=2, sharex=True, gridspec_kw={'height_ratios':[1,5]})
        fig.subplots_adjust(hspace=None)
        invisible_axes(ax[0])
        for sp in ['right', 'top']:
            ax[1].spines[sp].set_visible(False)
        ax[1].set_ylabel(ylabel)
        
        try:
            ax[1].plot(self.adj_ts, data1, color='blue')
        except: pass
        try:
            ax[1].plot(self.adj_ts, data2, color='m')
        except: pass
        
        try:
            ax[0].scatter(self.events, [1]*len(self.events), marker='|')
            ax[0].text(-10, 1, self.eventsVar.get(), va='center', ha='right')
        except AttributeError: pass

        ax[1].yaxis.set_major_formatter(StrMethodFormatter('{x:.1}'))
        ax[1].set_xlabel('Time (s)')

        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))

    def makesnips(self):
        # get events and number of bins from dropdown menus
        print("Making and plotting snips...")
        self.setevents()
        
        # extract snips and calculate noise from data      
        self.snips = mastersnipper(self.data, self.datauv, self.datafilt,
                                   self.fs,
                                   self.events,
                                   snipfs=float(self.fsnip.get()),
                                   preTrial=float(self.baseline.get()),
                                   trialLength=float(self.length.get()),
                                   threshold=float(self.noiseth.get()))
        print(self.snips.keys())
        self.noiseindex = self.snips['noise']
        self.pps = self.snips['info']['snipfs']

        self.snips_to_plot = self.snips[self.snipsVar.get()]
        if self.snipsVar.get() == 'filt_z':
            self.ylabel='Z-Score'
        else:
            self.ylabel='Delta F'
        
        self.maxtrials=np.shape(self.snips_to_plot)[0]
        self.getcurrenttrial()
        
        # plot data
        self.singletrialviewer()
        self.heatmapviewer()
        self.averagesnipsviewer()
        self.sessionviewer()
        
        if self.quickstart:
            if self.number_of_times == 0:
                tips('You can turn noise on and off with the "Toggle noise" button.')
                self.number_of_times = 1
            elif self.number_of_times == 1:
                tips('You can alter the baseline, snip length, sample frequency, and noise threshold by using the fields on the left.')
                self.number_of_times = 2
            elif self.number_of_times == 2:
                tips('You can export these data using the various Export / Save figs options at the bottom.')
                self.number_of_times = 3
            elif self.number_of_times == 3:
                tips('OK. Got it? Play around with the GUI as you see fit and if you notice bugs or would like added features let me know [j.mccutcheon@uit.no]')
                self.number_of_times = 4
    def setevents(self):
        try:
            tt_option = self.trialselectVar.get()
            if tt_option == "All":
                self.events = np.array(self.behavdf[self.eventsVar.get()]) - self.t0
            else:
                reduced_df = self.behavdf[self.behavdf[self.trialtypeVar.get()] == int(tt_option)]
                self.events = np.array(reduced_df[self.eventsVar.get()]) - self.t0
                if len(self.events) == 0:
                    print("Using all events...")
                    self.events = np.array(self.behavdf[self.eventsVar.get()]) - self.t0
        except:
            self.events = np.array(self.behavdf[self.eventsVar.get()]) - self.t0
                        
    def getcurrenttrial(self):
        try:
            trial_entered = int(self.currenttrial.get())
            if trial_entered < 1 or trial_entered > self.maxtrials:
                self.trial_to_plot = 'all'
            else:
                self.trial_to_plot = trial_entered-1
        except:
            self.trial_to_plot = 'all'
  
    def togglenoise(self):
        if self.noise:
            self.noise = False
            self.noiseBtn.config(text="Toggle noise")
            self.noiseBtn.state(['pressed'])
            self.addtoterminal(f"Noise set with threshold of {self.noisethField.get()} and noisy trials removed.\n")
        else:
            self.noise = True
            self.noiseBtn.config(text="Toggle noise")
            self.noiseBtn.state(['!pressed'])
            self.addtoterminal("Noisy trials included.\n")
            
        try:
            self.refresh()
        except: pass
    
    def toggletips(self):
        if self.quickstart:
            self.quickstart = False
            self.toggletipsBtn.state(['!pressed'])
        else:
            self.quickstart = True
            self.toggletipsBtn.state(['pressed'])
        
    def prevtrial(self):
        try:
            if int(self.currenttrial.get()) == 1:
                self.currenttrial.set(str(self.maxtrials))
            else:
                self.currenttrial.set(str(int(self.currenttrial.get()) - 1))
        except ValueError:
            self.currenttrial.set(str(self.maxtrials))
        self.addtoterminal(f"Showing trial {self.currenttrial.get()}.\n")
        self.refresh()
        
    def nexttrial(self):
        try:
            if int(self.currenttrial.get()) == self.maxtrials:
                self.currenttrial.set(str(1))  
            self.currenttrial.set(str(int(self.currenttrial.get()) + 1))
        except ValueError:
            self.currenttrial.set(str(1))
        self.addtoterminal(f"Showing trial {self.currenttrial.get()}.\n")
        self.refresh()
        
    def showall(self):
        self.addtoterminal('Showing all trials.\n')
        self.trial_to_plot = 'all'
        self.currenttrial.set('')
        self.refresh()

    def makelickruns(self):
        self.setlicks()
        self.runs={}
        self.runs[self.lickrunsVar.get()] = [val for i, val in enumerate(self.licks) if (val - self.licks[i-1] > 10)]
        self.epochfields.append('runs-' + self.lickrunsVar.get())
        self.updateeventoptions()

    def singletrialviewer(self):
        self.f_trials = Figure(figsize=(2.67,2.67)) # 5,3
        self.f_trials.subplotpars.left=0.3
        ax = self.f_trials.subplots()
        
        if self.trial_to_plot != 'all':
            trialsFig(ax, self.snips_to_plot[self.trial_to_plot][:], pps=self.pps,
                      eventText = self.eventsVar.get(),
                      ylabel=self.ylabel)
        else:
            if self.noise:
                trialsFig(ax, self.snips_to_plot, pps=self.pps, noiseindex=self.noiseindex,
                          preTrial=self.snips['info']['baseline'],
                          eventText = self.eventsVar.get(),
                          ylabel=self.ylabel)
            else:
                snips = np.asarray([i for (i,v) in zip(self.snips_to_plot, self.noiseindex) if not v])
                trialsFig(ax, snips, pps=self.pps, eventText = self.eventsVar.get(),
                          preTrial=self.snips['info']['baseline'],
                          ylabel=self.ylabel)
     
        canvas = FigureCanvasTkAgg(self.f_trials, self.f4)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))
        
    def heatmapviewer(self):
        self.f_heatmap = Figure(figsize=(2.67,2.67))
        self.f_heatmap.subplotpars.left=0.2
        ax = self.f_heatmap.add_subplot(111)
        
        if self.noise:
            snips=self.snips_to_plot
        else:
            snips=removenoise(self.snips_to_plot, self.noiseindex)
        
        makeheatmap(ax, snips, self.trial_to_plot, preTrial=self.snips['info']['baseline'], pps=self.pps)
        
        canvas = FigureCanvasTkAgg(self.f_heatmap, self.f5)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))
        
    def averagesnipsviewer(self):
        
        self.f_avgsnips = Figure(figsize=(2.67,2.67)) # 5.3
        self.f_avgsnips.subplotpars.left=0.3
        ax = self.f_avgsnips.subplots()
 
        if self.noise:
            snips=self.snips_to_plot
        else:
            snips=removenoise(self.snips_to_plot, self.noiseindex)

        trialsShadedFig(ax, snips,
                          self.pps,
                          eventText = self.eventsVar.get(),
                          preTrial=self.snips['info']['baseline'],
                          ylabel=self.ylabel)
        
        canvas = FigureCanvasTkAgg(self.f_avgsnips, self.f6)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))
    
    def chooseexportfolder(self):
        self.savefolder = Path(get_location())
    
    def makefilename(self):
        self.fileinfo = f"_{self.eventsVar.get()}{self.snipsVar.get()}_{self.suffix.get()}"
        
    def makeExcel(self):
        if not hasattr(self, 'savefolder'):
            self.chooseexportfolder()
        
        self.makefilename()
        savexlfile = self.savefolder / f"output{self.fileinfo}.xlsx"
        
        print('File saved as', savexlfile)
        
        self.terminal.insert(END, f'File saved as {savexlfile}')

        self.makesummarysheet()

        if self.noise:
            snips_to_write=self.snips_to_plot
            events_to_write=self.events
        else:
            snips_to_write=removenoise(self.snips_to_plot, self.noiseindex)
            events_to_write=[event for event, noise in zip(self.events, self.noiseindex) if not noise]
        
        wb = xl.Workbook(savexlfile)
        # worksheet with summary data
        sh = wb.add_worksheet('Summary')
        
        bold = wb.add_format({'bold': True})
        
        sh.set_column(0, 1, 20)
        sh.write('A1', 'Parameter', bold)
        sh.write('B1', 'Value', bold)
        for idx, vals in enumerate(self.d):
            sh.write(idx+1, 0, vals[0])
            sh.write(idx+1, 1, vals[1])
        
        # # worksheet with average trace
        sh = wb.add_worksheet('Average')
        
        for idx, val in enumerate(np.mean(snips_to_write, axis=0)):
            sh.write(idx, 0, val)
        
        # # worksheet with average trace
        sh = wb.add_worksheet('All trials')
        for idx in np.arange(len(snips_to_write[0])):
            for col, snip in enumerate(snips_to_write):
                sh.write(idx, col, snip[idx])

        sh = wb.add_worksheet('Event times')
        for col, event in enumerate(events_to_write):
            sh.write(0, col, event)

        wb.close()
        
    def makesummarysheet(self):
        
        self.d = [('Filename',str(self.tdtfile)),
                  ('Signal (470nm)',self.blue.get()),
                  ('Signal (405nm)',self.uv.get()),
                  ('Event',self.eventsVar.get()),
                  ('Onset or offset',self.trialtypeVar.get()),
                  ('Data type',self.snipsVar.get()),
                  ('Noise threshold',self.noisethVar.get()),
                  ('Noise on',self.noise)]
        
    def savefigs(self):
        if not hasattr(self, 'savefolder'):
            self.chooseexportfolder()
                
        self.makefilename()
        
        self.f_trials.savefig(self.savefolder / f"trials{self.fileinfo}.pdf")
        self.f_heatmap.savefig(self.savefolder / f"heatmap{self.fileinfo}.pdf")
        self.f_avgsnips.savefig(self.savefolder / f"averagesnips{self.fileinfo}.pdf")
        
        self.terminal.insert(END, f"Saving figures in {self.savefolder}")
        
    def addtoterminal(self, s):
        self.terminal.insert(END, s)
        self.terminal.see(END)
        print(s)

    # def getoutput(self, function):
    #     f = io.StringIO()
    #     with redirect_stdout(f):
    #         function()
    #     s = f.getvalue()
    #     self.addtoterminal(s)

def processdata_np(ca, iso, ts):
    cutoff = min(len(iso), len(ca), len(ts))
    
    iso = np.array(iso[:cutoff])
    ca = np.array(ca[:cutoff])
    
    t0 = ts[0]
    t = np.array(ts[:cutoff]) - t0
    
    iti = np.diff(t)

    ca_parms, parm_cov = curve_fit(exp_func, t, ca, p0=[1,1e-3,1],bounds=([0,0,0],[4,0.1,4]), maxfev=1000)
    ca_expfit = exp_func(t, *ca_parms)

    iso_parms, parm_cov = curve_fit(exp_func, t, iso, p0=[1,1e-3,1],bounds=([0,0,0],[4,0.1,4]), maxfev=1000)
    iso_expfit = exp_func(t, *iso_parms)
    
    ca_es = ca - ca_expfit
    iso_es = iso - iso_expfit
    
    slope, intercept, r_value, p_value, std_err = linregress(x=iso_es, y=ca_es)
    ca_est_motion = intercept + slope * iso_es
    ca_corrected = ca_es - ca_est_motion
    
    return ca_corrected
    
def exp_func(x, a, b, c):
   return a*np.exp(-b*x) + c

def start_photo_gui(quickstart=False):
    root = Tk()
    Grid.rowconfigure(root, 0, weight=1)
    Grid.columnconfigure(root, 0, weight=1)
    app = Window_photo(root, quickstart)

    root.lift()
    root.mainloop()
    
def tips(msg):
    print(msg)
    messagebox.showinfo('Quick Tips', msg)

if __name__ == '__main__':
    os.chdir("D:\\Test Data\\Johan\\")
    # os.chdir("D:\\Test Data\\data\\FiPho-180416\\")
    start_photo_gui(quickstart=False)
    