# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 10:24:11 2020

@author: James Edgar McCutcheon
"""

import numpy as np
import time
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from trompy import flatten_list, logical_subset, shadedError


def rocN(x,y,N=100):
    """ Function to calculate ROC based on MATLAB function
    
    Parameters
    -----------
    x, y : Arrays or lists of numerical data
        Data to be compared.
    N : Int, optional
        Number of bins to use for calculation. Deafault is 100.
        
    Returns
    --------
    a : Float
        ROC value. Number between 0 and 1.
    """
    if len(x) > 0 and len(y) >0:
        pass
    else:
        print("x and/or y are incorrect form")
        return np.NaN
    
    if len(x)<3 or len(y)<3:
        print('Too few trials for roc analysis!')
        return np.NaN
    
    zlo = np.min([np.min(x), np.min(y)])
    zhi = np.max([np.max(x), np.max(y)])
    z = np.linspace(zlo, zhi, N)

    fa, hit = [], []
    
    for i in range(N):
        fa.append(np.count_nonzero(y > z[i])) # faster than np.sum
        hit.append(np.count_nonzero(x > z[i]))
        
    fa.reverse()
    hit.reverse()
    
    fa = np.divide(fa, len(y))
    hit = np.divide(hit, len(x))
    
    fa[0], fa[-1] = 0, 1
    hit[0], hit[-1] = 0, 1
    
    a = np.trapz(fa, hit)
    
    return a
    
def rocshuf(x,y,nsims=10):
    """
    Performs ROC on shuffled data to obtain p-vlaue (probability) of observed ROC value
    
    Parameters
    -----------
    x, y : Arrays or lists of numerical data
        Data to be compared
    nsims : Int, optional
        Number of simulations to run. Precision of p-value will be increased by using a larger number (e.g. nsims=100 gives p-value to 0.01 precision). Default is 10.
        
    Returns
    ---------
    roc0 : Float
        ROC value. Number between 0 and 1.
    p : Float
        p-value.

    """
    z = x + y
    b = [True for val in x] + [False for val in y]
    n0 = len(b)

    roc0 = rocN(logical_subset(z, b), logical_subset(z, b, condition=False))
    
    a=[]
    for sim in range(nsims):
        I = np.random.permutation(n0)
        B = [b[idx] for idx in I]
        a.append(rocN(logical_subset(z, B), logical_subset(z, B, condition=False)))
 
    absa = np.abs(roc0 -0.5)
    p1 = len([val for val in a if val >= 0.5+absa])
    p2 = len([val for val in a if val <= 0.5-absa])
    
    p = p1/nsims + p2/nsims
    
    return roc0, p

def nanroc(x, y, N=100, min4roc=4, n4shuf=100):
    """
    Performs ROC analysis on multiple arrays or columns of data, e.g. for examining a time series.
    
    Parameters
    -----------
    x, y : Arrays or lists of numerical data
        Data to be compared
    N : Int, optional
        Number of bins for calculating ROC. Not currently used. Default is 100.
    min4roc : Int, optional
        Minimum number of data points for comparison. Not currently used. Default is 4.
    n4shuf : Int, optional
        Number of shuffled simulations to run to derive p-value. Precision of p-value will be increased by using a larger number (e.g. n4shuf=100 gives p-value to 0.01 precision). Default is 100.
        
    Returns
    ---------
    a : List of floats
        ROC values corresponding to each column in input data.
    p : List of floats
        p-values corresponding to each column in input data.
    """
 
    # checks dimensions of matrices
    if np.shape(x)[1] != np.shape(y)[1]:
        print('nanroc: matrices must have the same number of columns')
    
    a=[]
    p=[]
    
    for idx in range(np.shape(x)[1]):
        print(f"Analysing column {idx}")
        x0 = [val[idx] for val in x]
        x1 = [val[idx] for val in y]
        
        a0, p0 = rocshuf(x0, x1, nsims=n4shuf)
        
        a.append(a0)
        p.append(p0)
        
    return a, p

def run_roc_comparison(data, n4shuf=10, timer=True, savedata=""):
    """ Function to run ROC analysis with option for timing and saving resulting data
    
    Parameters
    -----------
    data : List or array of numerical values
        Two distributions to be compared. Normally should be of the shape (2,x,y) where x is number of trials and can be different
        between each array and y is bins and should be identical. Example, data[0] can be 300x20 list of lists or array and data[1] can
        be 360x20.
    n4shuf : Int, optional
        Number of times to repeat roc with shuffled values to calculate p-values. Default is 10, so that it is fast to run, but for accurate p-values should run 2000 times
    timer : Bool, optional
        Prints time taken if True
    savedata : Str, optional
        Filename for saving data. If empty, does not save anything. Default is ""
    
    Returns
    a : List of floats
        ROC values corresponding to each column in input data.
    p : List of floats
        p-values corresponding to each column in input data.
    
    """
    
    if timer: start_time = time.time()

    a, p = nanroc(data[0], data[1], n4shuf=n4shuf)
    
    if timer: print(f"--- Total ROC analysis took {(time.time() - start_time)} seconds ---")
    
    if len(savedata)>0:
        try:       
            pickle_out = open(savedata, 'wb')
            dill.dump([a, p, data], pickle_out)
            pickle_out.close()
        except:
            print("Cannot save. Check filename.")

    return a, p

def plot_ROC_and_line(f, a, p, snips1, snips2,
                      cdict=['grey', 'white', 'red'],
                      colors=['grey', 'red'],
                      labels=["", ""],
                      labeloffset_y=0,
                      labeloffset_x=0,
                      ylabel='',
                      xlabel='',
                      gridspec_dict=None,
                      ):
    """
    Makes ROC figure. Originally used to produce figures in Peters et al (2021)
    
    Parameters
    -----------
    f : Matplotlib figure object
        
    a, p : Lists of floats
        ROC values and p-values from ROC analysis
    snips1, snips2 : Lists or arrays of floats
        Binned data corresponding to the comparison that produced a and p
    cdict : List of 3 strings, optional
        Colors representing mapping of colors for representation of ROC values
    colors : List of 2 strings, optional
        Colors representing data from snips1 and snips2
    labels : List of 2 strings, optional
        Labels for snips1 and snips2
    labeloffset_y : Float, optional
        Specifies y label offset. Default is 0.
    labeloffset_x : Float, optional
        Specifies x label offset. Default is 0.
    ylabel : Str, optional
        Specifies y label
    xlabel : Str, optional
        Specifies x label
    gridspec_dict : Dict, optional
        Allows specification of figure and customisation.
        
    Returns
    ----------
    f, ax : Matplotlib figure and axis
    """
    
    ax=[]
    
    if type(gridspec_dict) == dict:
        try:
            gs_spec = gridspec_dict['gs_spec']
            gsx = gridspec_dict['gsx']
            gsy = gridspec_dict['gsy']
    
            gs = gs_spec[gsx, gsy].subgridspec(2,2, height_ratios=[0.25, 1], width_ratios=[1, 0.05], wspace=0.05)
        except:
            print('Problem with gridspec_dict when plotting ROC so ignoring it. Check it has correct keys.')
            return
    else:   
        gs=gridspec.GridSpec(2,2, figure=f, height_ratios=[0.25, 1], width_ratios=[1, 0.05], wspace=0.05,
                            bottom=0.2, right=0.75, left=0.15)
    
    ax.append(f.add_subplot(gs[0, 0]))
    
    # Creates colormap for ROC

    heatmap_color_scheme = LinearSegmentedColormap.from_list('rocmap', cdict)
    
    roc_for_plot = a + [0]
    xlen=len(snips1[0])
    xvals=np.arange(-0.5,xlen+0.5)
    yvals=[1, 2]
    xx, yy = np.meshgrid(xvals, yvals)
        
    mesh = ax[0].pcolormesh(xx, yy, [roc_for_plot, roc_for_plot], cmap=heatmap_color_scheme, shading = 'flat')
    mesh.set_clim([0, 1])
    
    threshold = 0.05/len(p)
    sigpoints = np.array([pval < threshold for pval in p], dtype=bool)
    
    if sum(sigpoints) > 0:
        xdata = [x for x, L in zip(range(len(sigpoints)), sigpoints) if L]
        ydata = logical_subset(a, sigpoints)
        ax[0].scatter(xdata, [2.5]*len(xdata), color='k', marker='.', clip_on=False)
    else:
        ax[0].scatter(2, 2.5, color='white', marker='.', clip_on=False)
    
    ax[0].text(-1, 2.5, 'p<0.05', va='center', ha='right')
    
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)
    ax[0].spines['left'].set_visible(False)
    ax[0].set_xticks([])
    ax[0].set_yticks([])
     
    cbar_ax = f.add_subplot(gs[0,1])   
    cbar = f.colorbar(mesh, cax=cbar_ax, ticks=[0, 1], label='ROC')
    
    ax.append(f.add_subplot(gs[1, 0]))
    
    shadedError(ax[1], snips1, linecolor=colors[0])
    shadedError(ax[1], snips2, linecolor=colors[1])
    
    ax[1].set_ylabel(ylabel)
    ax[1].spines['top'].set_visible(False)
    ax[1].spines['right'].set_visible(False)
    
    # ax[1].set_xticks([0, 10, 20, 30])
    # ax[1].set_xticklabels(['-10', '0', '10', '20'])
    ax[1].set_xlabel(xlabel)
    
    ax[1].text(xlen+labeloffset_x, np.mean(snips1, axis=0)[-1]-labeloffset_y, labels[0], color=colors[0], ha='left', va='center')
    ax[1].text(xlen+labeloffset_x, np.mean(snips2, axis=0)[-1]+labeloffset_y, labels[1], color=colors[1], ha='left', va='center')
    
    ax[0].set_xlim(ax[1].get_xlim())
    
    return f, ax