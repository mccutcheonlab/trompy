# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:23:32 2020

@author: James Edgar McCutcheon
"""
import matplotlib.pyplot as plt
import numpy as np

def trialsFig(ax, trials, pps=1, preTrial=10, scale=5, noiseindex = [],
              plotnoise=True,
              eventText='event', 
              ylabel=''):
    """ Plots single trials and mean (e.g. photometry signaL timelocked to an event).
    
    Parameters
    -----------
    ax : Matplotlib axis object
        Axis where data will be plotted.
    trials : List of list of floats or 2D array
        Data to be plotted where rows are individual trials and columns are time bins.
    pps : Int, optional
        Points per second. Default is 1.
    preTrial : Int or Float, optional
        Time (generally in seconds) preceding timelocked event. Default is 10.
    scale : Int, optional
        Scale bar length in seconds, Default is 5.
    noiseindex : List of Booleans, optional
        Can provide indices of trials that exceed a certain threshold for exclusion. Deafult is [].
    plotnoise : Bool, optional
        If False, will exclude any trials provided as indices in noise index. Default is True.
    eventText : Str, optional
        Text on graph can be customized, e.g. Pellet. Default is "event".
    ylabel : Str, optional
        Text for y-axis label. Default is "".
    
    Returns
    --------
    ax : Matplotlib axis object
        Axis object is returned. 
    """

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
    """ Plots single trials from multiple datasets (e.g. photometry signaL timelocked to an event).
    
    Parameters
    -----------
    ax : Matplotlib axis object
        Axis where data will be plotted.
    trials : Tuple of list of list of floats or 3D array
        Data to be plotted of shape (2,x,y) where first dimension is different datasets.
    pps : Int, optional
        Points per second. Default is 1.
    preTrial : Int or Float, optional
        Time (generally in seconds) preceding timelocked event. Default is 10.
    scale : Int, optional
        Scale bar length in seconds, Default is 5.
    ylabel : Str, optional
        Text for y-axis label. Default is "".
    linecolor : List of two strings, optional
        Colors to use for plotting different datasets. Default is ['m', 'b'] (magenta and blue).
    
    Returns
    --------
    ax : Matplotlib axis object
        Axis object is returned.
        
    Notes
    ------
    Not used very often. May need to be revised to be more functional.
    """    
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
    
    """ Plots multiple trials as a shaded error plot (e.g. photometry signaL timelocked to an event).

    Parameters
    -----------
    ax : Matplotlib axis object
        Axis where data will be plotted.
    trials : List of list of floats or 2D array
        Data to be plotted where rows are individual trials and columns are time bins.
    pps : Int, optional
        Points per second. Default is 1.
    scale : Int, optional
        Scale bar length in seconds, Default is 5.
    preTrial : Int or Float, optional
        Time (generally in seconds) preceding timelocked event. Default is 10.
    noiseindex : List of Booleans, optional
        Can provide indices of trials that exceed a certain threshold for exclusion. Deafult is [].
    eventText : Str, optional
        Text on graph can be customized, e.g. Pellet. Default is "event".
    ylabel : Str, optional
        Text for y-axis label. Default is "".
    linecolor : Str, optional
        Color to use for plotting mean. Default is "k" (black).
    errorcolor : Str, optional
        Color to plot shaded error in. Default is "grey".

    Returns
    --------
    ax : Matplotlib axis object
        Axis object is returned.
    """
    
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
    """ Plots two different datasets as multiple trials with shaded error plot (e.g. photometry signaL timelocked to an event).
     
    Parameters
    -----------
    ax : Matplotlib axis object
        Axis where data will be plotted.
    trials : Tuple of list of list of floats or 3D array
        Data to be plotted of shape (2,x,y) where first dimension is different datasets.
    pps : Int, optional
        Points per second. Default is 1.
    scale : Int, optional
        Scale bar length in seconds, Default is 5.
    preTrial : Int or Float, optional
        Time (generally in seconds) preceding timelocked event. Default is 10.
    noiseindex : List of ints, optional
        Can provide indices of trials that exceed a certain threshold for exclusion. Deafult is [].
    eventText : Str, optional
        Text on graph can be customized, e.g. Pellet. Default is "event".
    ylabel : Str, optional
        Text for y-axis label. Default is "".
    linecolor : List of two strings, optional
        Colors to use for plotting means. Default is ['m', 'b'] (magenta and blue).
    errorcolor : List of two strings, optional
        Colors to plot shaded error in. Default is ['r', 'g'] (red and green).
    title : Str, optional
        Title for plot. Default is "".

    Returns
    --------
    ax : Matplotlib axis object
        Axis object is returned.
    """
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
    """ Plots individual trials as tiles. Good for searching for good representative figures.
    
    Parameters
    -----------
    gs : gridspec object
    trials : List of lists of floats or 2D array
    pps : Int, optional
    preTrial : Int
    
    Notes
    ------
    Not well tested. May need work.    
    """
    for i in np.arange(np.shape(trials)[0]):
        col=int(i/7)
        row=(i%7)+1

        ax = plt.subplot(gs[row, col])
        ax.plot(trials[i,:].transpose(), c='grey', alpha=0.4)   

        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

def makeheatmap(ax, data, trial_to_plot="all", preTrial=10, pps=1, events=None, ylabel='Trial'):
    """ For making trial-by-trial heatmaps.
    
    Parameters
    -------------
    ax : Matplotlib axis object
        Axis to plot data in.
    data : List of list of floats or 2D array
        Data to be plotted where rows are individual trials and columns are time bins.
    trial_to_plot : Int or Str, optional
        Will place tick on specific trial if argument passed. Default is "all".
    preTrial : Int or Float, optional
        Time (generally in seconds) preceding timelocked event. Default is 10.
    pps : Int, optional
        Points per second. Default is 1.
    events : List of floats, optional
        Allows event times to be passed (e.g. latencies) which will be marked as white lines on heatplot.
    ylabel : Str, optional
        Label for y-axis. Default is "".
        
    Returns
    ---------
    ax : Matplotlib axis object
    mesh : Matplotlib mesh object
    
    """
    (ntrials, bins) = np.shape(data)

    xvals = np.linspace(-preTrial+(1/pps),(bins/pps)-preTrial,bins)
    yvals = np.arange(1, ntrials+2)
    xx, yy = np.meshgrid(xvals, yvals)
    
    mesh = ax.pcolormesh(xx, yy, data, cmap='jet', shading = 'auto')
    
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