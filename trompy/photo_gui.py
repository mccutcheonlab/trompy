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
from pathlib import Path

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
        self.savefigsBtn = ttk.Button(self, text='Save Figs', command=self.savefigs)

        # Label definitions
        self.shortfilename = StringVar(self.master)
        self.shortfilename.set('No tank chosen')
        self.filenameLbl = ttk.Label(self, textvariable=self.shortfilename, wraplength=200)
        self.timelockLbl = ttk.Label(self, text='--Timelocked event--')
        
        self.primarysigLbl = ttk.Label(self, text='Primary signal')
        self.autofsigLbl = ttk.Label(self, text='AutoFl. signal')
        
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
        
        self.choosefileBtn.grid(column=0, row=0, rowspan=2, sticky=(N,S,E,W))
        self.loaddataBtn.grid(column=0, row=2,rowspan=2, sticky=(N,S,E,W))
        self.filenameLbl.grid(column=0, row=4, rowspan=2, sticky=(E,W))
        self.timelockLbl.grid(column=0, row=4, rowspan=2, sticky=(E,W))
        
        self.primarysigLbl.grid(column=1, row=0)
        self.autofsigLbl.grid(column=1, row=2)
        
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
        
        self.chooseblueMenu.grid(column=1, row=1)
        self.chooseuvMenu.grid(column=1, row=3)

    def updateeventoptions(self):
        try:
            eventOptions = self.epochfields
            lickrunOptions = self.epochfields
        except AttributeError:
            eventOptions = ['None']
            lickrunOptions = ['None']
        
        self.chooseeventMenu = ttk.OptionMenu(self, self.eventsVar, eventOptions[0], *eventOptions)
        self.chooseeventMenu.grid(column=0, row=6)

        snipOptions = ['blue', 'uv', 'filt', 'filt_z']
        self.choosesnipMenu = ttk.OptionMenu(self, self.snipsVar, snipOptions[0], *snipOptions)
        self.choosesnipMenu.grid(column=6, row=12)
   
        onsetOptions = ['onset', 'offset', 'runs', 'random', 'notes']
        self.onsetMenu = ttk.OptionMenu(self, self.onsetVar, onsetOptions[0], *onsetOptions)
        self.onsetMenu.grid(column=1, row=6)
        
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
        except AttributeError: # This is necessary as a workaround for streams that begin with an underscore
            tmp = tdt.read_block(self.tdtfile, evtype=['streams'])
            self.data = getattr(tmp.streams, self.blue.get())['data']
            self.fs = getattr(tmp.streams, self.blue.get())['fs']
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
        
        # extract snips and calculate noise from data      
        self.snips = mastersnipper(self.data, self.datauv, self.datafilt,
                                   self.fs,
                                   self.events,
                                   snipfs=float(self.fsnip.get()),
                                   preTrial=float(self.baseline.get()),
                                   trialLength=float(self.length.get()),
                                   threshold=float(self.noiseth.get()))
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
        
    def setevents(self):
        try:
            self.eventepoc = getattr(self.epocs, self.eventsVar.get())
            if self.onsetVar.get() == 'onset' or self.onsetVar.get() == 'offset':
                try:
                   self.events = getattr(self.eventepoc, self.onsetVar.get())
                except AttributeError:
                    alert(f'{self.eventsVar.get()} does not have {self.onsetVar.get()}')
            elif self.onsetVar.get() == 'runs':
                try:
                    tmp = getattr(self.eventepoc, 'onset')
                    self.events = [val for i, val in enumerate(tmp) if (val - tmp[i-1]) > float(self.baseline.get())]
                except:
                    alert(f'Cannot calculate runs for {self.eventsVar.get()}')
            elif self.onsetVar.get() == 'random':
                try:
                    nevents = len(getattr(self.eventepoc, 'onset'))
                    if nevents > 100:
                        nevents = 100
                    elif nevents < 10:
                        nevents = 10
                except AttributeError:
                    nevents = 30
                print(f'Creating {nevents} random events.')
                self.events = list(np.sort(np.random.randint(low=120, high=int(len(self.data)/self.fs)-120, size=30)))
            elif self.onsetVar.get() == 'notes':
                try:
                    self.events = self.eventepoc.notes.ts
                except:
                    alert('Could not find notes.')
                    
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

        self.makesummarysheet()

        if self.noise:
            snips_to_write=self.snips_to_plot
        else:
            snips_to_write=removenoise(self.snips_to_plot, self.noiseindex)
        
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

        wb.close()
        
    def makesummarysheet(self):
        
        self.d = [('Filename',self.tdtfile),
                  ('Signal (470nm)',self.blue.get()),
                  ('Signal (405nm)',self.uv.get()),
                  ('Event',self.eventsVar.get()),
                  ('Onset or offset',self.onsetVar.get()),
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

def start_photo_gui():
    root = Tk()
    app = Window_photo(root)
    root.lift()
    root.mainloop()

if __name__ == '__main__':
    os.chdir("C:\\Github\\PPP_analysis\\data\\Eelke-171027-111329\\")
    os.chdir("C:\\Test Data\\data\\FiPho-180416\\")
    start_photo_gui()
    