# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:18:05 2020

@author: admin
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.cbook as cbook
import matplotlib.mlab as mlab
import colorsys

def setsameaxislimits(axes, axis='y'):
    axmin = []
    axmax = []
    for ax in axes:
        axmin.append(ax.get_ylim()[0])
        axmax.append(ax.get_ylim()[1])
    min_axmin = np.min(axmin)
    max_axmax = np.max(axmax)
    
    for ax in axes:
        ax.set_ylim([min_axmin, max_axmax])
#                sclist.append(ax.plot(x, y, '-o', markersize = scattersize/10,
#                         color = scatterlinecolor,
#                         markerfacecolor = scf,
#                         markeredgecolor = sce))
        
def invisible_axes(ax):
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    for sp in ['left', 'right', 'top', 'bottom']:
        ax.spines[sp].set_visible(False)

def shadedError(ax, yarray, linecolor='black', errorcolor = 'xkcd:silver', linewidth=1):
    yarray = np.array(yarray)
    y = np.mean(yarray, axis=0)
    yerror = np.std(yarray)/np.sqrt(len(yarray))
    x = np.arange(0, len(y))
    ax.plot(x, y, color=linecolor, linewidth=1)
    ax.fill_between(x, y-yerror, y+yerror, color=errorcolor, alpha=0.4)
    
    return ax

def ax2prop(axlims, n):
    """
    axlims should be provided as result of ax.get_xlims()
    n should be a list of values to convert
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

    Examples:
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

    def _kde_method(X, coords):
        # fallback gracefully if the vector contains only one value
        if np.all(X[0] == X):
            return (X[0] == coords).astype(float)
        kde = mlab.GaussianKDE(X, bw_method)
        return kde.evaluate(coords)

    vpstats = cbook.violin_stats(dataset, _kde_method, points=points)
    return vpstats