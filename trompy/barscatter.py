# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 09:19:56 2020

@author: James Edgar McCutcheon
"""
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain, count

def barscatter(data, transpose = False,
                groupwidth = .75,
                barwidth = .8,
                paired = False,
                unequal = False,
                spaced = False,
                yspace = 20,
                xspace = 0.1,
                barfacecoloroption = 'same', # other options 'between' or 'individual'
                barfacecolor = ['white'],
                baredgecoloroption = 'same',
                baredgecolor = ['black'],
                baralpha = 1,
                scatterfacecoloroption = 'same',
                scatterfacecolor = ['white'],
                scatteredgecoloroption = 'same',
                scatteredgecolor = ['grey'],
                scatterlinecolor = 'grey', # Don't put this value in a list
                scattersize = 80,
                scatteralpha = 1,
                spreadscatters = False,
                linewidth=0.75,
                xlim=[],
                ylim=[],
                ylabel = 'none',
                xlabel = 'none',
                grouplabel = 'auto',
                itemlabel = 'none',
                barlabels = [],
                barlabeloffset=0.025,
                grouplabeloffset=0,
                yaxisparams = 'auto',
                show_legend = 'none',
                legendloc='upper right',
                xfontsize=8,
                ax=[]):
    """
    Creates a bar graph with data points shown as overlaid circles.
    
    Parameters
    -------------
    data : List, lists of lists or array
        Data to be plotted. Will try to convert if needed.
    barwidth : Float, optional
        Width of bars. Default is 0.9.
    paired : Bool, optional
        Attempts to add lines between paired data points. Requires number in each group to be matched. Default is False.
    unequal : Bool, optional
        To be set to True if groups are unequal. Default is False.
    spaced : Bool, optional
        Spaces out data points so that they are not at an identical x value, e.g. grape bunch style. Default is False.
    yspace : Int or Float, optional
        Used in conjunction with spaced to determine spacing of data points. Default is 20.
    xspace : Float, optional
        Used in conjunction with spaced to determine spacing of data points. Default is 0.1.
    barfacecoloroption : Str, optional
        Chooses bar color option. Default is 'same' and other options are 'between' or 'individual'.
    barfacecolor : List of str, optional
        If 'between' or 'individual' is chosen for above option then number of colors needs to match number of bars or groups. Default is ['white'].
    baredgecoloroption : Str, optional
        Chooses bar edge option. Default is 'same', see notes on barfacecoloroption.
    baredgecolor : List of str, optional
        Bar edge colors. Default is ['black'], see notes on barfacecolor.
    baralpha : Float, optional
        Sets opacity of bars so must be between 0 and 1. Default is 1.
    scatterfacecoloroption : Str, optional
        Chooses scatter face option. Default is 'same', see notes on barfacecoloroption.
    scatterfacecolor : List of str, optional
        Scatter face colors. Default = ['white'], see notes on barfacecolor.
    scatteredgecoloroption : Str, optional
        Chooses scatter edge option. Default is 'same', see notes on barfacecoloroption.
    scatteredgecolor : List of str, optional
        Scatter face colors. Default is ['grey'], see notes on barfacecolor.
    scatterlinecolor : Str, optional
        Color of lines connecting related data points, should not be in a list. Default is 'grey'.
    scattersize : Int or Float, optional
        Size of datapoints. Default is 80.
    scatteralpha : Float, optional
        Sets opacity of scatter points. Default is 1.
    spreadscatters : Bool, optional
        Not currently functional. Needs to be checked.
    linewidth : Float, optional
        Width of lines. Default is 0.75.
    xlim : List or 2-tuple of floats, optional
        Sets limits of x-axis. Default is [].
    ylim : List or 2-tuple of floats, optional
        Sets limits of x-axis. Default is [].
    ylabel : Str, optional
        Sets y-axis label. Default is 'none'.
    xlabel : Str, optional
        Sets x-axis label. Default is 'none'.
    grouplabel : List of str, optional
        Sets labels for each group. Default is 'auto'.
    itemlabel : List of str, optional
        Not currently functional. Needs to be checked. Default is 'none'.
    barlabels : List of str, optional
        Sets labels for each bar. Default is [].
    barlabeloffset : Float, optional
        Sets barlabel offset relative to x baseline. Default is 0.025.
    grouplabeloffset : Float, optional
        Sets grouplabel offset relative to x baseline. Default is 0.0250.
    yaxisparams : None, optional
        Not currently functional. Needs to be checked.
    show_legend : Bool or str, optional
        Shows legend. Default is 'none'.
    legendloc : Str, optional
        Sets legend location. Default is 'upper right'.
    xfontsize : Int, optional
        Sets x-axis font size. Default is 8.
    ax : Matplotlib axis object, optional
        Axis object to plot in. If not provided, plots in new figure/axis. Default is [].
    
    Returns
    -------------
    ax : Matplotlib axis object
        Axis object of plot.
    barx : List of floats
        x-values where each bar is plotted.
    barlist : List of bar container objects
        Allows modifcation, e.g. changing of colors of individual bars. See notes.
    sclist : List of scatter container objects
        Allows modifcation as described above. See notes.
    """

    if unequal == True:
        dims = np.ndim(data)
        data_obj = np.ndarray((np.shape(data)), dtype=object)
        if dims == 1:
            for i, dim in enumerate(data):
                data_obj[i] = np.array(dim, dtype=object)
            data = data_obj
        elif dims == 2:            
            for i1, dim1 in enumerate(data):
                for i2, dim2 in enumerate(dim1):
                    data_obj[i1][i2] = np.array(dim2, dtype=object)
            data = data_obj
        else:
            print('Cannot convert that number of dimensions or data is in wrong format. Attmepting to make graph assuming equal groups.')
    
    if type(data) != np.ndarray or data.dtype != object:
        dims = np.shape(data)
        if len(dims) == 2 or len(dims) == 1:
            data = data2obj1D(data)

        elif len(dims) == 3:
            data = data2obj2D(data)
              
        else:
            print('Cannot interpret data shape. Should be 2 or 3 dimensional array. Exiting function.')
            return

    # Check if transpose = True
    if transpose == True:
        data = np.transpose(data)
        
    # Initialize arrays and calculate number of groups, bars, items, and means
    
    barMeans = np.zeros((np.shape(data)))
    items = np.zeros((np.shape(data)))
    
    nGroups = np.shape(data)[0]
    groupx = np.arange(1,nGroups+1)

    if len(np.shape(data)) > 1:
        grouped = True
        barspergroup = np.shape(data)[1]
        barwidth = (barwidth * groupwidth) / barspergroup
        
        for i in range(np.shape(data)[0]):
            for j in range(np.shape(data)[1]):
                barMeans[i][j] = np.mean(data[i][j])
                items[i][j] = len(data[i][j])
        
    else:
        grouped = False
        barspergroup = 1
        
        for i in range(np.shape(data)[0]):
            barMeans[i] = np.mean(data[i])
            items[i] = len(data[i])
    
    # Calculate x values for bars and scatters
    
    xvals = np.zeros((np.shape(data)))
    barallocation = groupwidth / barspergroup
    k = (groupwidth/2) - (barallocation/2)
    
    if grouped == True:
        
        for i in range(np.shape(data)[0]):
            xrange = np.linspace(i+1-k, i+1+k, barspergroup)
            for j in range(barspergroup):
                xvals[i][j] = xrange[j]
    else:
        xvals = groupx
    
    # Set colors for bars and scatters
     
    barfacecolorArray = setcolors(barfacecoloroption, barfacecolor, barspergroup, nGroups, data)
    baredgecolorArray = setcolors(baredgecoloroption, baredgecolor, barspergroup, nGroups, data)
     
    scfacecolorArray = setcolors(scatterfacecoloroption, scatterfacecolor, barspergroup, nGroups, data, paired_scatter = paired)
    scedgecolorArray = setcolors(scatteredgecoloroption, scatteredgecolor, barspergroup, nGroups, data, paired_scatter = paired)
    
    # Initialize figure
    if ax == []:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    # Make bars
    barlist = []
    barx = []
    for x, y, bfc, bec in zip(xvals.flatten(), barMeans.flatten(),
                              barfacecolorArray, baredgecolorArray):
        barx.append(x)
        barlist.append(ax.bar(x, y, barwidth,
                         facecolor = bfc, edgecolor = bec,
                         zorder=-1,
                         linewidth=linewidth))
    
    # Uncomment these lines to show method for changing bar colors outside of
    # function using barlist properties
    #for i in barlist[2].get_children():
    #    i.set_color('r')
    
    # Make scatters
    sclist = []
    if paired == False:
        for x, Yarray, scf, sce  in zip(xvals.flatten(), data.flatten(),
                                        scfacecolorArray, scedgecolorArray):
            if spaced == True:
                try: 
                    xVals, yVals = xyspacer(ax, x, Yarray, bindist=yspace, space=xspace)
                except:
                    print("Could not space all sets of points.")
                    xVals = [x] * len(Yarray)
                    yVals = Yarray
                    
                sclist.append(ax.scatter(xVals, yVals, s = scattersize,
                             c = scf,
                             edgecolors = sce,
                             linewidth=linewidth,
                             zorder=20,
                             clip_on=False))
                         
            else:
                for y in Yarray:
                     sclist.append(ax.scatter(x, y, s = scattersize,
                                     c = scf,
                                     edgecolors = sce,
                                     linewidth=linewidth,
                                     zorder=20,
                                     clip_on=False))
                     
    elif grouped == True:
        for x, Yarray, scf, sce in zip(xvals, data, scfacecolorArray, scedgecolorArray):
            for y in np.transpose(Yarray.tolist()):
                sclist.append(ax.plot(x, y, '-o', markersize = scattersize/10,
                         color = scatterlinecolor,
                         linewidth=linewidth,
                         markerfacecolor = scf,
                         markeredgecolor = sce,
                         markeredgewidth=linewidth,
                         zorder=20,
                         clip_on=False))
    elif grouped == False:
        for n,_ in enumerate(data[0]):
            y = [y[n-1] for y in data]
            sclist.append(ax.plot(xvals, y, '-o', markersize = scattersize/10,
                         color = scatterlinecolor,
                         linewidth=linewidth,
                         markerfacecolor = scfacecolorArray[0],
                         markeredgecolor = scedgecolorArray[0],
                         markeredgewidth=linewidth,
                         zorder=20,
                         clip_on=False))
    
    # Label axes
    if ylabel != 'none':
        ax.set_ylabel(ylabel)
    
    if xlabel != 'none':
        ax.set_xlabel(xlabel)
    
    # Set range and tick values for Y axis
    if yaxisparams != 'auto':
        ax.set_ylim(yaxisparams[0])
        ax.set_yticks(yaxisparams[1])
        
    ax.yaxis.set_tick_params(width=linewidth)

    # X ticks
    ax.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,
        labelbottom=False) # labels along the bottom edge are off
    
    ax.set_xticks([])

    if len(xlim) > 0:
        ax.set_xlim(xlim)
    if len(ylim) > 0:
        ax.set_ylim(ylim)
        
    xrange = ax.get_xlim()[1] - ax.get_xlim()[0]
    yrange = ax.get_ylim()[1] - ax.get_ylim()[0]
        
    if grouplabel == 'auto':
        ax.tick_params(labelbottom='off')
    else:
        ax.tick_params(labelbottom='off')

        groupx = np.arange(1, len(grouplabel)+1)
        if len(xlim) > 0:
            groupx = [x for x in groupx]
        xpos = (groupx - ax.get_xlim()[0])/xrange

        for x, label in zip(xpos, grouplabel):
            ax.text(x, -0.05+grouplabeloffset, label, va='top', ha='center', fontsize=xfontsize, transform=ax.transAxes)
        
    if len(barlabels) > 0:
        if len(barlabels) != len(barx):
            print('Wrong number of bar labels for number of bars!')
        else:
            xpos = (barx - ax.get_xlim()[0])/xrange
            ypos = (-ax.get_ylim()[0]/yrange) - barlabeloffset

            for x, label in zip(xpos, barlabels):
                ax.text(x, ypos, label, va='top', ha='center', fontsize=xfontsize, transform=ax.transAxes)

    # Hide the right and top spines and set bottom to zero
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_position('zero')

    ax.spines['bottom'].set_lw(linewidth)
    ax.spines['left'].set_lw(linewidth)
    
    if show_legend == 'within':
        if len(itemlabel) != barspergroup:
            print('Not enough item labels for legend!')
        else:
            legendbar = []
            legendtext = []
            for i in range(barspergroup):
                legendbar.append(barlist[i])
                legendtext.append(itemlabel[i])
            ax.legend(legendbar, legendtext, loc=legendloc)
    
    
    
    return ax, barx, barlist, sclist
      
def setcolors(coloroption, colors, barspergroup, nGroups, data, paired_scatter = False):
    """ Helper function for setting colors in barscatter"""
            
    nColors = len(colors)
    
    if (paired_scatter == True) & (coloroption == 'within'):
        print('Not possible to make a Paired scatter plot with Within setting.')
        coloroption = 'same'
        
    if coloroption == 'within':
        if nColors < barspergroup:
            print('Not enough colors for this option! Reverting to one color.')
            coloroption = 'same'
        elif nColors > barspergroup:
            colors = colors[:barspergroup]
        coloroutput = [colors for i in data]
        coloroutput = list(chain(*coloroutput))
        
    if coloroption == 'between':
        if nColors < nGroups:
            print('Not enough colors for this option! Reverting to one color.')
            coloroption = 'same'
        elif nColors > nGroups:
            colors = colors[:nGroups]
        if paired_scatter == False:
            coloroutput = [[c]*barspergroup for c in colors]
            coloroutput = list(chain(*coloroutput))
        else:
            coloroutput = colors
            
    if coloroption == 'individual':
        if nColors < nGroups*barspergroup:
            print('Not enough colors for this color option')
            coloroption = 'same'
        elif nColors > nGroups*barspergroup:
            coloroutput = colors[:nGroups*barspergroup]
        else: 
            coloroutput = colors
    
    if coloroption == 'same':
        coloroutput = [colors[0] for x in range(len(data.flatten()))]

    return coloroutput

def data2obj1D(data):
    """ Helper function for barscatter for converting data into apporopriate structure"""
    obj = np.empty(len(data), dtype=object)
    for i,x in enumerate(data):
        obj[i] = np.array(x)  
    return obj

def data2obj2D(data):
    """ Helper function for barscatter for converting data into apporopriate structure"""
    obj = np.empty((np.shape(data)[0], np.shape(data)[1]), dtype=object)
    for i,x in enumerate(data):
        for j,y in enumerate(x):
            obj[i][j] = np.array(y)
    return obj

def xyspacer(ax, x, yvals, bindist=20, space=0.1):
    """ Helper function for barscatter for spacing individual datapoints"""
    
    histrange=[]
    histrange.append(min(ax.get_ylim()[0], min(yvals)))
    histrange.append(max(ax.get_ylim()[1], max(yvals)))

    yhist = np.histogram(yvals, bins=bindist, range=histrange)
    
    xvals=[]
    for ybin in yhist[0]:
        if ybin == 1:
            xvals.append(x)
        elif ybin > 1:          
            temp_vals = np.linspace(x-space, x+space, num=ybin)
            for val in temp_vals:
                xvals.append(val)
                
    yvals = np.sort(yvals)

    return xvals, yvals

if __name__ == "__main__":
    barscatter([[1, 2, 3, 4], [5, 6, 7, 8]], paired=True)