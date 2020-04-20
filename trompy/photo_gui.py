# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:22:07 2020

@author: admin
"""

# Import statements
import sys
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import string
import numpy as np
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import StrMethodFormatter
import ntpath
import csv
import collections
import tdt
import xlsxwriter as xl

from trompy import *

# Main class for GUI
class Window_photo(Frame):
    
    def __init__(self, master=None):
        f1 = ttk.Style()
        f1.configure('.', background='powder blue', padding=5)
        f1.configure('TButton', width=15, sticky=(E,W))
        f1.configure('TEntry', width=7)
        f2 = ttk.Style()
        f2.configure('inner.TFrame', background='light cyan')
        
        ttk.Frame.__init__(self, master, style='TFrame', padding=(10, 10, 15, 15))               
        
        self.master = master        
        self.init_window()

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

        # Button definitions
        self.choosefileBtn = ttk.Button(self, text='Choose Tank', command=self.choosefile)
        self.loaddataBtn = ttk.Button(self, text='Load data', command=self.loaddata)
        self.makelickrunsBtn = ttk.Button(self, text='Lick runs', command=self.makelickruns)
        self.makesnipsBtn = ttk.Button(self, text='Make Snips', command=self.makesnips)
        self.noiseBtn = ttk.Button(self, text='Turn noise off', command=self.togglenoise)
        self.prevtrialBtn = ttk.Button(self, text='Prev Trial', command=self.prevtrial)
        self.nexttrialBtn = ttk.Button(self, text='Next Trial', command=self.nexttrial)
        self.showallBtn = ttk.Button(self, text='Show All', command=self.showall)
        self.refreshBtn = ttk.Button(self, text='Refresh', command=self.makesnips)
        self.defaultfolderBtn = ttk.Button(self, text='Default folder', command=self.chooseexportfolder)
        self.makeexcelBtn = ttk.Button(self, text='Make Excel', command=self.makeExcel)

        # Label definitions
        self.shortfilename = StringVar(self.master)
        self.shortfilename.set('No tank chosen')
        self.filenameLbl = ttk.Label(self, textvariable=self.shortfilename, wraplength=200)
        
        self.baselineLbl = ttk.Label(self, text='Baseline (s)')
        self.lengthLbl = ttk.Label(self, text='Snipit length (s)')
        self.nbinsLbl = ttk.Label(self, text='No. of bins')
        self.noisethLbl = ttk.Label(self, text='Noise threshold')
        
        self.suffixLbl = ttk.Label(self, text='File suffix')
        
        # Field and entries
        self.baseline = StringVar(self.master)
        self.baselineField = ttk.Entry(self, textvariable=self.baseline)
        self.baselineField.insert(END, '10')

        self.length = StringVar(self.master)
        self.lengthField = ttk.Entry(self, textvariable=self.length)
        self.lengthField.insert(END, '30')
        
        self.nbins = StringVar(self.master)
        self.nbinsField = ttk.Entry(self, textvariable=self.nbins)
        self.nbinsField.insert(END, '300')
        
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

        self.aboutLbl = ttk.Label(self, text='Photometry Analyzer-2.3 by J McCutcheon')

        
        # Packing grid with widgets
        self.f2.grid(column=2, row=0, columnspan=3, rowspan=3, sticky=(N,S,E,W))
        self.f3.grid(column=5, row=0, columnspan=3, rowspan=3, sticky=(N,S,E,W))
        self.f4.grid(column=2, row=4, columnspan=2, rowspan=5, sticky=(N,S,E,W))
        self.f5.grid(column=4, row=4, columnspan=2, rowspan=5, sticky=(N,S,E,W))
        self.f6.grid(column=6, row=4, columnspan=2, rowspan=5, sticky=(N,S,E,W))
        
        self.choosefileBtn.grid(column=0, row=0)
        self.loaddataBtn.grid(column=0, row=1)
        self.filenameLbl.grid(column=0, row=2, columnspan=2, sticky=W)
        
        self.makelickrunsBtn.grid(column=1, row=4)
        
        self.baselineLbl.grid(column=0, row=5, sticky=E)
        self.baselineField.grid(column=1, row=5)
        self.lengthLbl.grid(column=0, row=6, sticky=E)
        self.lengthField.grid(column=1, row=6)
        self.nbinsLbl.grid(column=0, row=7, sticky=E)
        self.nbinsField.grid(column=1, row=7)
        self.noisethLbl.grid(column=0, row=8, sticky=E)
        self.noisethField.grid(column=1, row=8)
        
        self.prevtrialBtn.grid(column=2, row=9)
        self.nexttrialBtn.grid(column=2, row=10)
        self.currenttrialField.grid(column=3, row=9)
        self.showallBtn.grid(column=3, row=10, sticky=(W, E))
        
        self.refreshBtn.grid(column=7, row=9, sticky=(W, E))
        
        self.makesnipsBtn.grid(column=9, row=4, rowspan=2, sticky=(N, S, W,E))
        self.noiseBtn.grid(column=9, row=6, rowspan=2, sticky=(N, S, W,E))
        
        self.aboutLbl.grid(column=0, row=11, columnspan=3, sticky=W)
        self.progress.grid(column=0, row=12, columnspan=2, sticky=(W, E))
        
        self.suffixLbl.grid(column=2, row=12, sticky=E)
        self.suffixField.grid(column=3, row=12, sticky=(W, E))
        self.defaultfolderBtn.grid(column=4, row=12, sticky=(W, E))
        self.makeexcelBtn.grid(column=5, row=12, sticky=(W, E))
     
        self.blue = StringVar(self.master)       
        self.uv = StringVar(self.master)  
        self.eventsVar = StringVar(self.master)
        self.onsetVar = StringVar(self.master)
        self.lickrunsVar = StringVar(self.master)
        self.snipsVar = StringVar(self.master)
        self.noisethVar = IntVar(self.master)
        self.noise=True
        
        self.updatesigoptions()
        self.updateeventoptions()
        
        self.sessionviewer()
        
        #self.quickstart()
        
    def quickstart(self):
        self.choosefile()
        self.loaddata()
        
    def choosefile(self):
        self.tdtfile = filedialog.askdirectory(initialdir=os.getcwd(), title='Select a tank.')
        self.shortfilename.set(ntpath.dirname(self.tdtfile))
        
        print(self.shortfilename.get())
        # opens file to get stream and epoch names
        self.getstreamandepochnames()
        
        # update dropdown menu options
        self.updatesigoptions()
        self.updateeventoptions()
    
    def getstreamandepochnames(self):
        tmp = tdt.read_block(self.tdtfile, t2=2, evtype=['streams'])
        self.streamfields = [v for v in vars(tmp.streams) if v != 'Fi2r']
        
        tmp = tdt.read_block(self.tdtfile, evtype=['epocs'])
        self.epocs = getattr(tmp, 'epocs')
        self.epochfields = [v for v in vars(self.epocs)]
        
    def updatesigoptions(self):
        try:
            sigOptions = self.streamfields
        except AttributeError:
            sigOptions = ['None']
            
        self.chooseblueMenu = ttk.OptionMenu(self, self.blue, sigOptions[0], *sigOptions)
        self.chooseuvMenu = ttk.OptionMenu(self, self.uv, sigOptions[0], *sigOptions)
        
        self.chooseblueMenu.grid(column=1, row=0)
        self.chooseuvMenu.grid(column=1, row=1)

    def updateeventoptions(self):
        try:
            eventOptions = self.epochfields
            lickrunOptions = self.epochfields
        except AttributeError:
            eventOptions = ['None']
            lickrunOptions = ['None']
        
        self.chooseeventMenu = ttk.OptionMenu(self, self.eventsVar, eventOptions[0], *eventOptions)
        self.chooseeventMenu.grid(column=0, row=3)

        snipOptions = ['blue', 'uv', 'filt', 'filt_z']
        self.choosesnipMenu = ttk.OptionMenu(self, self.snipsVar, snipOptions[0], *snipOptions)
        self.choosesnipMenu.grid(column=6, row=9)
   
        onsetOptions = ['onset', 'offset']
        self.onsetMenu = ttk.OptionMenu(self, self.onsetVar, onsetOptions[0], *onsetOptions)
        self.onsetMenu.grid(column=1, row=3)

        self.chooselicksMenu = ttk.OptionMenu(self, self.lickrunsVar, lickrunOptions[0], *lickrunOptions)
        self.chooselicksMenu.grid(column=0, row=4)
        
    def loaddata(self):   
        self.progress['value'] = 0
        
        self.progress['value'] = 40
        # load in streams
        self.loadstreams()
        self.progress['value'] = 60
        
        # process data
        self.datafilt = processdata(self.data, self.datauv, normalize=True)
        self.progress['value'] = 80
        
        # set time vectors
        self.t2sMap = time2samples(self.data, self.fs)
        self.progress['value'] = 90
        
        # plot all session data
        self.sessionviewer()
        self.progress['value'] = 100
        
    def loadstreams(self):
        try:
            tmp = tdt.read_block(self.tdtfile, evtype=['streams'], store=self.blue.get())
            self.data = getattr(tmp.streams, self.blue.get())['data']
            self.fs = getattr(tmp.streams, self.blue.get())['fs']
            
            tmp = tdt.read_block(self.tdtfile, evtype=['streams'], store=self.uv.get())
            self.datauv = getattr(tmp.streams, self.uv.get())['data']
        except:
            print('No file chosen yet or problem extracting signals')

    def sessionviewer(self):
        try:
            self.makesessionfig(self.f2, self.data, self.datauv, 'F')
        except AttributeError:
            self.makesessionfig(self.f2, [], [], 'F')
            
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
            ax[1].plot(self.t2sMap, data1, color='blue')
        except: pass
        try:
            ax[1].plot(self.t2sMap, data2, color='m')
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
        self.setevents()
        self.bins = int(self.nbins.get())
        
        # extract snips and calculate noise from data      
        self.randomevents = makerandomevents(120, max(self.t2sMap)-120)
        self.bgTrials, self.pps = snipper(self.data, self.randomevents,
                                        t2sMap = self.t2sMap, fs = self.fs, bins=self.bins)
        self.snips = mastersnipper(self.data, self.datauv, self.datafilt,
                                   self.t2sMap, self.fs,
                                   self.events,
                                   bins=int(self.bins),
                                   preTrial=int(self.baseline.get()),
                                   trialLength=int(self.length.get()),
                                   threshold=int(self.noiseth.get()))
        self.noiseindex = self.snips['noise']

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
        
    def setevents(self):
        try:
            if 'runs' in self.eventsVar.get():
                key=self.eventsVar.get().split('-')
                self.events = self.runs[key[1]]
            else:
                self.eventepoc = getattr(self.epocs, self.eventsVar.get())
                self.events = getattr(self.eventepoc, self.onsetVar.get())
        except:
            alert('Cannot set events')
            
    def setlicks(self):
        try:
            self.lickepoc = getattr(self.epocs, self.lickrunsVar.get())
            self.licks = getattr(self.lickepoc, self.onsetVar.get())
        except:
            alert('Cannot set licks')
            
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
            self.noiseBtn.config(text="Turn noise on")
        else:
            self.noise = True
            self.noiseBtn.config(text="Turn noise off")
            
        try:
            self.makesnips()
        except: pass
        
    def prevtrial(self):
        try:
            if int(self.currenttrial.get()) == 1:
                self.currenttrial.set(str(self.maxtrials))
            else:
                self.currenttrial.set(str(int(self.currenttrial.get()) - 1))
        except ValueError:
            self.currenttrial.set(str(self.maxtrials))
        self.makesnips()
        
    def nexttrial(self):
        try:
            if int(self.currenttrial.get()) == self.maxtrials:
                self.currenttrial.set(str(1))  
            self.currenttrial.set(str(int(self.currenttrial.get()) + 1))
        except ValueError:
            self.currenttrial.set(str(1))
        self.makesnips()
        
    def showall(self):
        print('Showing all trials')
        self.trial_to_plot = 'all'
        self.currenttrial.set('')
        self.makesnips()

    def makelickruns(self):
        self.setlicks()
        self.runs={}
        self.runs[self.lickrunsVar.get()] = [val for i, val in enumerate(self.licks) if (val - self.licks[i-1] > 10)]
        self.epochfields.append('runs-' + self.lickrunsVar.get())
        self.updateeventoptions()

    def singletrialviewer(self):
        f = Figure(figsize=(2.67,2.67)) # 5,3
        f.subplotpars.left=0.3
        ax = f.subplots()
        
        if self.trial_to_plot != 'all':
            trialsFig(ax, self.snips_to_plot[self.trial_to_plot][:], pps=self.pps,
                      eventText = self.eventsVar.get(),
                      ylabel=self.ylabel)
        else:
            if self.noise:
                trialsFig(ax, self.snips_to_plot, pps=self.pps, noiseindex=self.noiseindex,
                          eventText = self.eventsVar.get(),
                          ylabel=self.ylabel)
            else:
                snips = np.asarray([i for (i,v) in zip(self.snips_to_plot, self.noiseindex) if not v])
                trialsFig(ax, snips, pps=self.pps, eventText = self.eventsVar.get(),
                          ylabel=self.ylabel)
     
        canvas = FigureCanvasTkAgg(f, self.f4)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))
        
    def heatmapviewer(self):
        f = Figure(figsize=(2.67,2.67))
        f.subplotpars.left=0.2
        ax = f.add_subplot(111)
        
        if self.noise:
            snips=self.snips_to_plot
        else:
            snips=np.asarray([i for (i,v) in zip(self.snips_to_plot, self.noiseindex) if not v])
        
        makeheatmap(ax, snips, self.trial_to_plot)
        
        canvas = FigureCanvasTkAgg(f, self.f5)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))
        
    def averagesnipsviewer(self):
        
        f = Figure(figsize=(2.67,2.67)) # 5.3
        f.subplotpars.left=0.3
        ax = f.subplots()
 
        if self.noise:
            snips=self.snips_to_plot
        else:
            snips=np.asarray([i for (i,v) in zip(self.snips_to_plot, self.noiseindex) if not v])

        trialsShadedFig(ax, snips,
                          self.pps,
                          eventText = self.eventsVar.get(),
                          ylabel=self.ylabel)
        
        canvas = FigureCanvasTkAgg(f, self.f6)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(N,S,E,W))
    
    def chooseexportfolder(self):
        self.savefolder = get_location()
        
        print(self.shortfilename.get())
        
    def makeExcel(self):
        if not hasattr(self, 'savefolder'):
            self.chooseexportfolder()
            
        savefile = self.savefolder + '//' + 'output_' + self.suffix.get() + '.xlsx'
        
        print(savefile)
        
#        try:
        self.makesummarysheet()
        
        wb = xl.Workbook(savefile)
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
        self.makeaveragesnips()
        
        for idx, val in enumerate(self.averagesnips):
            sh.write(idx, 0, val)
        
        # sh = wb.add_worksheet('ILIs')
        # for idx, val in enumerate(self.lickdata['ilis']):
        #     sh.write(idx, 0, val)

        # sh = wb.add_worksheet('Bursts')
        # for idx, val in enumerate(self.lickdata['bLicks']):
        #     sh.write(idx, 0, val)
            
        wb.close()
#        except:
#            alert('Working on making an Excel file')

    def makesummarysheet(self):
        
        self.d = [('Filename',self.tdtfile),
                  ('Signal (470nm)',self.blue.get()),
                  ('Signal (405nm)',self.uv.get()),
                  ('Event',self.eventsVar.get()),
                  ('Onset or offset',self.onsetVar.get()),
                  ('Data type',self.snipsVar.get()),
                  ('Noise threshold',self.noisethVar.get()),
                  ('Noise on',self.noise)]

    def makeaveragesnips(self):
        if self.noise:
            snips=self.snips_to_plot
        else:
            snips=np.asarray([i for (i,v) in zip(self.snips_to_plot, self.noiseindex) if not v])
            
        self.averagesnips = np.mean(snips, axis=0)

def start_photo_gui():
    root = Tk()
    app = Window_photo(root)
    root.lift()
    root.mainloop()

if __name__ == '__main__':
    start_photo_gui()
    