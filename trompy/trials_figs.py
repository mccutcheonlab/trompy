# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:23:32 2020

@author: admin
"""
import matplotlib.pyplot as plt
import numpy as np

def trialsFig(ax, trials, pps=1, preTrial=10, scale=5, noiseindex = [],
              plotnoise=True,
              eventText='event', 
              ylabel=''):

    if len(noiseindex) > 0:
        trialsNoise = np.array([i for (i,v) in zip(trials, noiseindex) if v])
        trials = np.array([i for (i,v) in zip(trials, noiseindex) if not v])
        if plotnoise == True:
            ax.plot(trialsNoise.transpose(), c='red', alpha=0.1)
        
    ax.plot(trials.transpose(), c='grey', alpha=0.4)
    ax.plot(np.mean(trials,axis=0), c='k', linewidth=2)
     
    ax.set(ylabel = ylabel)
    ax.xaxis.set_visible(False)
            
    scalebar = scale * pps

    yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
    scalebary = (yrange / 10) + ax.get_ylim()[0]
    scalebarx = [ax.get_xlim()[1] - scalebar, ax.get_xlim()[1]]
    
    ax.plot(scalebarx, [scalebary, scalebary], c='k', linewidth=2)
    ax.text((scalebarx[0] + (scalebar/2)), scalebary-(yrange/50), str(scale) +' s', ha='center',va='top')
 
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    xevent = pps * preTrial  
    ax.plot([xevent, xevent],[ax.get_ylim()[0], ax.get_ylim()[1] - yrange/20],'--')
    ax.text(xevent, ax.get_ylim()[1], eventText, ha='center',va='bottom')
    
    return ax

def trialsMultFig(ax, trials, pps=1, preTrial=10, scale=5,
              eventText='event', 
              ylabel='',
              linecolor=['m', 'b'],):
    
    for i in [0, 1]:
        y = trials[i].transpose()   
        ax.plot(y, c=linecolor[i], linewidth=1)
     
    ax.set(ylabel = ylabel)
    ax.xaxis.set_visible(False)
            
    scalebar = scale * pps

    yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
    scalebary = (yrange / 10) + ax.get_ylim()[0]
    scalebarx = [ax.get_xlim()[1] - scalebar, ax.get_xlim()[1]]
    
    ax.plot(scalebarx, [scalebary, scalebary], c='k', linewidth=2)
    ax.text((scalebarx[0] + (scalebar/2)), scalebary-(yrange/50), str(scale) +' s', ha='center',va='top')
 
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    xevent = pps * preTrial
    ax.plot([xevent, xevent],[ax.get_ylim()[0], ax.get_ylim()[1] - yrange/20],'--')
    ax.text(xevent, ax.get_ylim()[1], eventText, ha='center',va='bottom')
    
    return ax

def trialsShadedFig(ax, trials, pps = 1, scale = 5, preTrial = 10,
                    noiseindex=[],
                    eventText = 'event', ylabel = '',
                    linecolor='k', errorcolor='grey'):
    
    if len(noiseindex) > 0:
        trials = np.array([i for (i,v) in zip(trials, noiseindex) if not v])
    
    yerror = [np.std(i)/np.sqrt(len(i)) for i in trials.T]
    y = np.mean(trials,axis=0)
    x = np.arange(0,len(y))
    
    ax.plot(x, y, c=linecolor, linewidth=2)

    errorpatch = ax.fill_between(x, y-yerror, y+yerror, color=errorcolor, alpha=0.4)
    
    ax.set(ylabel = ylabel)
    ax.xaxis.set_visible(False)
            
    scalebar = scale * pps

    yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
    scalebary = (yrange / 10) + ax.get_ylim()[0]
    scalebarx = [ax.get_xlim()[1] - scalebar, ax.get_xlim()[1]]
    
    ax.plot(scalebarx, [scalebary, scalebary], c='k', linewidth=2)
    ax.text((scalebarx[0] + (scalebar/2)), scalebary-(yrange/50), '5 s', ha='center',va='top')
 
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    xevent = pps * preTrial
    ax.plot([xevent, xevent],[ax.get_ylim()[0], ax.get_ylim()[1] - yrange/20],'--')
    ax.text(xevent, ax.get_ylim()[1], eventText, ha='center',va='bottom')
    
    return ax, errorpatch

def trialsMultShadedFig(ax, trials, pps = 1, scale = 5, preTrial = 10,
                        noiseindex=[],
                        eventText = 'event', ylabel = '',
                        linecolor=['m', 'b'], errorcolor=['r', 'g'],
                        title=''):

    for i in [0, 1]:
        if len(noiseindex) > 0:
            trials[i] = np.array([i for (i,v) in zip(trials[i], noiseindex) if not v])
        yerror = [np.std(i)/np.sqrt(len(i)) for i in trials[i].T]
        y = np.mean(trials[i],axis=0)
        x = np.arange(0,len(y))
    
        ax.plot(x, y, c=linecolor[i], linewidth=2)

        errorpatch = ax.fill_between(x, y-yerror, y+yerror, color=errorcolor[i], alpha=0.4)
    
    ax.set(ylabel = ylabel)
    ax.xaxis.set_visible(False)
            
    scalebar = scale * pps

    yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
    scalebary = (yrange / 10) + ax.get_ylim()[0]
    scalebarx = [ax.get_xlim()[1] - scalebar, ax.get_xlim()[1]]
    
    ax.plot(scalebarx, [scalebary, scalebary], c='k', linewidth=2)
    ax.text((scalebarx[0] + (scalebar/2)), scalebary-(yrange/50), '5 s', ha='center',va='top')
 
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    xevent = pps * preTrial
    ax.plot([xevent, xevent],[ax.get_ylim()[0], ax.get_ylim()[1] - yrange/20],'--')
    ax.text(xevent, ax.get_ylim()[1], eventText, ha='center',va='bottom')
    ax.set_title(title)
    
    return ax, errorpatch

def trialstiledFig(gs, trials, pps = 1, preTrial = 10):
    for i in np.arange(np.shape(trials)[0]):
        col=int(i/7)
        row=(i%7)+1

        ax = plt.subplot(gs[row, col])
        ax.plot(trials[i,:].transpose(), c='grey', alpha=0.4)   

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

def makeheatmap(ax, data, trial_to_plot, events=None, ylabel='Trial'):
    ntrials = np.shape(data)[0]
    xvals = np.linspace(-9.9,20,300)
    yvals = np.arange(1, ntrials+2)
    xx, yy = np.meshgrid(xvals, yvals)
    
    mesh = ax.pcolormesh(xx, yy, data, cmap='jet', shading = 'flat')
    
    if events:
        ax.vlines(events, yvals[:-1], yvals[1:], color='w')
    else:
        print('No events')
        
    ax.set_ylabel(ylabel)
    if trial_to_plot == 'all':
        ax.set_yticks([1, ntrials])
    else:
        ax.set_yticks([1, trial_to_plot+1, ntrials])
    ax.set_xticks([])
    ax.invert_yaxis()
    
    return ax, mesh