# %%
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:18:05 2020

@author: James Edgar McCutcheon
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.cbook as cbook
import matplotlib.mlab as mlab
import colorsys

def setsameaxislimits(axes, axis='y'):

    """ Sets same y axis limits for all axis objects passed.
    
    Parameters
    -----------
    axes : List of Matplotlib axis objects
        One or more axis objects to be equalized.
    axis : Str, optional
        Non-functional but will be added in future. Default is "y".
    """
    axmin = []
    axmax = []
    for ax in axes:
        axmin.append(ax.get_ylim()[0])
        axmax.append(ax.get_ylim()[1])
    min_axmin = np.min(axmin)
    max_axmax = np.max(axmax)
    
    for ax in axes:
        ax.set_ylim([min_axmin, max_axmax])
        
def invisible_axes(ax):
    """ Sets axes to invisible. """
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    for sp in ['left', 'right', 'top', 'bottom']:
        ax.spines[sp].set_visible(False)

def shadedError(ax, yarray, linecolor='black', errorcolor = 'xkcd:silver', linewidth=1,
                    linestyle="-", alpha=0.4, **kwargs):
    """ Simple shaded error plot.
    
    Parameters
    ------------
    ax : Matplotlib axis object
        Axis where data will be plotted.
    yarray : 2D array or List of list of floats
        Data to be plotted where rows are individual trials and columns are time bins.
    linecolor : Str, optional
        Color that average (mean) will be plotted in. Default is "black".
    errorcolor : Str, optional
        Color that shaded error area will be. Default is "xkcd:silver".
    linewidth : Float or int, optional
        Line width for average (mean). Default is 1.
    linestyle : Str, optional
        Line style for average. Default is solid ("-").
    alpha : Float, optional
        Transparency of error. Should be between 0 and 1. Default is 0.4.
        
    Returns
    ----------
    ax : Matplotlib axis object
    """
    yarray = np.array(yarray)
    y = np.mean(yarray, axis=0)
    yerror = np.std(yarray, axis=0)/np.sqrt(len(yarray))
    x = np.arange(0, len(y))
    ax.plot(x, y, color=linecolor, linewidth=linewidth, linestyle=linestyle)
    ax.fill_between(x, y-yerror, y+yerror, color=errorcolor, alpha=alpha)
    
    return ax

def ax2prop(axlims, n):
    """ Scales values relative to axis limits, e.g. for determining where events should be plotted on an axis.
    
    Parameters
    ------------
    axlims : Tuple or lust with 2 elements
        Normally the result of ax.get_xlims()
    n : List of floats
        Values that should be scaled relative to axis limits.
        
    Returns
    ---------
    output : List of floats
        Scaled values.
    """
    axrange = axlims[1] - axlims[0]
    output = []
    for n in n:
        output.append((n - axlims[0])/axrange)
        
    return output

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    
    Parameters
    -------------
    color : Str
        Color to be lightened
    amount : Float, optional
        Amount to lighten color by. Default is 0.5.
        
    Examples
    -------------
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """

    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

def get_violinstats(dataset, points=100, bw_method=None):

    """ Gets stats for a violin plot.
    
    Parameters
    ------------
    dataset : List or array of floats
        Dataset for constructing violin plot.
    points : Int, optional
        Number of points for caclulating violin plot. Default is 100.
    bw_method : Str, optional
        Bandwidth method for calculating violin plot. Default is None.
        
    Returns
    ---------
    vpstats : Structured array
    
    """

    def _kde_method(X, coords):
        # fallback gracefully if the vector contains only one value
        if np.all(X[0] == X):
            return (X[0] == coords).astype(float)
        kde = mlab.GaussianKDE(X, bw_method)
        return kde.evaluate(coords)

    vpstats = cbook.violin_stats(dataset, _kde_method, points=points)
    return vpstats

if __name__ == "__main__":
    data = np.random.random([50,100])
    f, ax = plt.subplots()
    shadedError(ax, data, linestyle="--")
# %%
