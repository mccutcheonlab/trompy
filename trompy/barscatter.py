# -*- coding: utf-8 -*-
# %##
"""
Created on Fri Apr 17 09:19:56 2020

@author: James Edgar McCutcheon
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import chain

import trompy as tp

class BarScatter():
    def __init__(self, data, linewidth, fontsize, bar_kwargs, sc_kwargs, ax_kwargs, extra_kwargs):
        self.data = np.asarray(data, dtype=object)

        self.linewidth = linewidth
        self.fontsize = fontsize

        self.bar_kwargs = bar_kwargs
        self.sc_kwargs = sc_kwargs
        self.ax_kwargs = ax_kwargs
        self.extra_kwargs = extra_kwargs

    def create_axis(self, ax):
        if isinstance(ax, plt.Axes):
            self.ax = ax
        else:
            f, self.ax = plt.subplots()

    def squeeze(self):
        if np.shape(self.data)[0] == 1:
            self.data = np.squeeze(self.data)
            self.squeeze()
        else:
            return

    def set_dims(self):
        # self.squeeze()
        self.grouped=False
        self.dims = np.ndim(self.data)
        self.n_groups = np.shape(self.data)[0]

        if self.dims == 1:
            try:
                self.data[0][0]
                self.dims = 2
            except:
                self.n_groups = 1
        elif self.dims == 2:
            try:
                self.data[0][0][0]
                self.grouped = True
                self.dims = 3
            except:
                pass
        elif self.dims == 3:
            self.grouped = True

    def prep_data(self, transpose=False):

        self.set_dims()

        data_obj = np.ndarray((np.shape(self.data)[:self.dims-1]), dtype=object)
        if self.grouped:
            for i1, dim1 in enumerate(self.data):
                for i2, dim2 in enumerate(dim1):
                    data_obj[i1][i2] = list(dim2)
            self.data = data_obj
        else:
            for i, dim in enumerate(self.data):
                data_obj[i] = list(dim)
            self.data = data_obj

        # Check if transpose = True
        if transpose:
            self.data = np.transpose(self.data)

    def calculate_items(self, barwidth, groupwidth):

        self.group_width = groupwidth
        self.group_x = np.arange(1,self.n_groups+1)
        self.bar_means = np.zeros((np.shape(self.data)[:self.dims-1]))
        self.bar_error = np.zeros((np.shape(self.data)[:self.dims-1]))

        if self.grouped:
            self.bars_per_group = np.shape(self.data)[1]
            self.width_of_bars = (barwidth * groupwidth) / self.bars_per_group
                
            for i in range(np.shape(self.data)[0]):
                for j in range(np.shape(self.data)[1]):
                    self.bar_means[i][j], self.bar_error[i][j] = tp.mean_and_sem(self.data[i][j])
        else:
            self.bars_per_group = 1
            self.width_of_bars = barwidth

            for i in range(np.shape(self.data)[0]):
                self.bar_means[i], self.bar_error[i] = tp.mean_and_sem(self.data[i])

    def calculate_x_vals(self):

        self.x_vals = np.zeros((np.shape(self.data)[:self.dims-1]))
        bar_allocation = self.group_width / self.bars_per_group
        k = (self.group_width/2) - (bar_allocation/2)
        
        if self.grouped == True:
            
            for i in range(np.shape(self.data)[0]):
                xrange = np.linspace(i+1-k, i+1+k, self.bars_per_group)
                for j in range(self.bars_per_group):
                    self.x_vals[i][j] = xrange[j]
        else:
            self.x_vals = self.group_x

    def set_colors(self, color_option, colors, paired_scatter = False):
        """ Helper function for setting colors in barscatter"""
            
        n_colors = len(colors)
        
        if (paired_scatter == True) & (color_option == 'within'):
            print('Not possible to make a Paired scatter plot with Within setting.')
            color_option = 'same'
            
        if color_option == 'within':
            if n_colors < self.bars_per_group:
                print('Not enough colors for this option! Reverting to one color.')
                color_option = 'same'
            elif n_colors > self.bars_per_group:
                colors = colors[:self.bars_per_group]
            color_output = [colors for i in self.data]
            color_output = list(chain(*color_output))
            
        if color_option == 'between':
            if n_colors < self.n_groups:
                print('Not enough colors for this option! Reverting to one color.')
                color_option = 'same'
            elif n_colors > self.n_groups:
                colors = colors[:self.n_groups]
            if paired_scatter == False:
                color_output = [[c]*self.bars_per_group for c in colors]
                color_output = list(chain(*color_output))
            else:
                color_output = colors
                
        if color_option == 'individual':
            if n_colors < self.n_groups*self.bars_per_group:
                print('Not enough colors for this color option')
                color_option = 'same'
            elif n_colors > self.n_groups*self.bars_per_group:
                color_output = colors[:self.n_groups * self.bars_per_group]
            else: 
                color_output = colors
        
        if color_option == 'same':
            color_output = [colors[0] for x in range(len(self.data.flatten()))]

        return color_output

    def xyspacer(self, x, y_vals, bindist=20, space=0.1):
        """ Helper function for barscatter for spacing individual datapoints"""

        histrange=[]
        histrange.append(min(self.ax.get_ylim()[0], min(y_vals)))
        histrange.append(max(self.ax.get_ylim()[1], max(y_vals)))

        yhist = np.histogram(y_vals, bins=bindist, range=histrange)

        self.x_vals=[]
        for ybin in yhist[0]:
            if ybin == 1:
                self.x_vals.append(x)
            elif ybin > 1:          
                temp_vals = np.linspace(x-space, x+space, num=ybin)
                for val in temp_vals:
                    self.x_vals.append(val)
                    
        self.y_vals = np.sort(y_vals)
    
    def make_bars(self, errorbars):
        self.barlist = []
        self.barx = []
        for x, y, e, bfc, bec in zip(self.x_vals.flatten(), self.bar_means.flatten(), self.bar_error.flatten(),
                                self.barfacecolorArray, self.baredgecolorArray):
            self.barx.append(x)
            if errorbars == True:
                self.bar_kwargs.update({"yerr": e})
            self.barlist.append(self.ax.bar(x, y, self.width_of_bars,
                            facecolor = bfc, edgecolor = bec,
                            zorder=-1,
                            linewidth=self.linewidth,
                            **self.bar_kwargs))
    
    def make_scatters(self, paired, spaced, xspace, yspace, scatterlinecolor, scattersize, scatteroffset):
        self.sclist = []
        self.x_vals =  self.x_vals + (scatteroffset*self.width_of_bars)/2
        
        if paired == False:
            for x, Yarray, scf, sce  in zip(self.x_vals.flatten(), self.data.flatten(),
                                            self.scfacecolorArray, self.scedgecolorArray):
                if spaced == True:
                    try:
                        self.xyspacer(x, Yarray, bindist=yspace, space=xspace)
                    except:
                        print("Could not space all sets of points.")
                        self.x_vals = [x] * len(Yarray)
                        self.y_vals = Yarray
                        
                    self.sclist.append(self.ax.scatter(self.x_vals, self.y_vals, s = scattersize,
                                c = scf,
                                edgecolors = sce,
                                **self.sc_kwargs))
                            
                else:
                    for y in Yarray:
                        self.sclist.append(self.ax.scatter(x, y, s = scattersize,
                                        c = scf,
                                        edgecolors = sce,
                                        **self.sc_kwargs))
                        
        elif self.grouped == True:
            for x, Yarray, scf, sce in zip(self.x_vals, self.data, self.scfacecolorArray, self.scedgecolorArray):
                for y in np.transpose(Yarray.tolist()):
                    self.sclist.append(self.ax.plot(x, y, '-o', markersize = scattersize/10,
                            color = scatterlinecolor,
                            markerfacecolor = scf,
                            markeredgecolor = sce,
                            markeredgewidth = self.sc_kwargs["linewidth"],
                            **self.sc_kwargs))
        elif self.grouped == False:
            for n,_ in enumerate(self.data[0]):
                y = [y[n-1] for y in self.data]
                self.sclist.append(self.ax.plot(self.x_vals, y, '-o', markersize = scattersize/10,
                            color = scatterlinecolor,
                            markerfacecolor = self.scfacecolorArray[0],
                            markeredgecolor = self.scedgecolorArray[0],
                            markeredgewidth = self.sc_kwargs["linewidth"],
                            **self.sc_kwargs))

    def set_axis_properties(self):


        self.ax.set(**self.ax_kwargs)
        self.xrange = np.diff(self.ax.get_xlim())
        self.yrange = np.diff(self.ax.get_ylim())

    def format_ticks(self):
        for axis in [self.ax.yaxis, self.ax.xaxis]:
            axis.set_tick_params(width=self.linewidth)
        self.ax.set_xticks([])
        self.ax.tick_params(labelbottom='off')
    
    def tidy_axes(self):
    
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_position('zero')

        self.ax.spines['bottom'].set_lw(self.linewidth)
        self.ax.spines['left'].set_lw(self.linewidth)
    
    def make_group_labels(self, grouplabel, grouplabeloffset):
        group_x = np.arange(1, len(grouplabel)+1)

        xpos = (group_x - self.ax.get_xlim()[0]) / self.xrange

        for x, label in zip(xpos, grouplabel):
            self.ax.text(x, -0.05+grouplabeloffset, label, va='top', ha='center', fontsize=self.fontsize, transform=self.ax.transAxes)

    def make_bar_labels(self, barlabels, barlabeloffset):
        xpos = (self.barx - self.ax.get_xlim()[0]) / self.xrange
        ypos = (-self.ax.get_ylim()[0]/self.yrange) - barlabeloffset

        for x, label in zip(xpos, barlabels):
            self.ax.text(x, ypos, label, va='top', ha='center', fontsize=self.fontsize, transform=self.ax.transAxes)

    def make_legend(self, itemlabels, legendloc):
        legendbar = []
        legendtext = []
        for i in range(self.bars_per_group):
            legendbar.append(self.barlist[i])
            legendtext.append(itemlabels[i])
        self.ax.legend(legendbar, legendtext, loc=legendloc)

    def process_kwargs(self):
        if "baralpha" in self.extra_kwargs.keys():
            self.bar_kwargs.update({"alpha": self.extra_kwargs["baralpha"]})

        if "scatteralpha" in self.extra_kwargs.keys():
            self.sc_kwargs.update({"alpha": self.extra_kwargs["scatteralpha"]})

        self.sc_kwargs.update({"linewidth": self.linewidth, "zorder": 20, "clip_on": False})

        legacy_ax_props = ["xlabel", "ylabel", "xlim", "ylim"]
        for prop in legacy_ax_props:
            if prop in self.extra_kwargs:
                self.ax_kwargs[prop] = self.extra_kwargs[prop]

        functional_kwargs = ["xlabel", "ylabel", "xlim", "ylim", "baralpha", "scatteralpha"]
        for key in self.extra_kwargs.keys():
            if key not in functional_kwargs:
                warnings.warn("{} is not a functional keyword argument. Check spelling or barscatter version.".format(key))

def barscatter(data_in, ax=[], transpose=False, paired=False,
               spaced=False, xspace=0.1, yspace=20,
               groupwidth = .75, barwidth = .8,
               barfacecolor_option="same", barfacecolor=["white"],
               baredgecolor_option="same", baredgecolor=["black"],
               errorbars=False, scatteroffset=0,
               scatterfacecolor_option="same", scatterfacecolor=["white"],
               scatteredgecolor_option="same", scatteredgecolor=["black"],
               scatterlinecolor="grey", linewidth=0.75, scattersize=80,
               grouplabel=[], grouplabeloffset=0,
               barlabels=[], barlabeloffset=0.025,
               itemlabels=[], show_legend=False, legendloc="upper right",
               fontsize=10,
               bar_kwargs={},
               sc_kwargs={},
               ax_kwargs={},
               **extra_kwargs):

    bs = BarScatter(data_in, linewidth, fontsize, bar_kwargs, sc_kwargs, ax_kwargs, extra_kwargs)

    bs.process_kwargs()

    bs.prep_data(transpose=transpose)
    bs.calculate_items(barwidth, groupwidth)
    bs.calculate_x_vals()

    bs.barfacecolorArray = bs.set_colors(barfacecolor_option, barfacecolor)
    bs.baredgecolorArray = bs.set_colors(baredgecolor_option, baredgecolor)

    bs.scfacecolorArray = bs.set_colors(scatterfacecolor_option, scatterfacecolor)
    bs.scedgecolorArray = bs.set_colors(scatteredgecolor_option, scatteredgecolor)

    bs.create_axis(ax)

    bs.make_bars(errorbars)

    bs.make_scatters(paired, spaced, xspace, yspace, scatterlinecolor, scattersize, scatteroffset)

    bs.set_axis_properties()
    bs.format_ticks()
    bs.tidy_axes()

    if len(grouplabel) == bs.n_groups:
        bs.make_group_labels(grouplabel, grouplabeloffset)
    
    if len(barlabels) == len(bs.barx):
        bs.make_bar_labels(barlabels, barlabeloffset)

    if show_legend:
        if len(itemlabels) == len(bs.barx):
            bs.make_legend(itemlabels, legendloc)
        elif len(barlabels) == len(bs.barx):
            bs.make_legend(barlabels, legendloc)
        else:
            barlabels=[str(x) for x in np.arange(1, len(bs.barx)+1)]
            bs.make_legend(barlabels, legendloc)
    
    return bs.ax, bs.barx, bs.barlist, bs.sclist


# #TODO change markerstyle
# #TODO read pandas series, dataframe etc
# #TODO add extra axis for estimation
# #TODO make sure fontsize is for all arguments
# #TODO make labels without offsets
# #TODO add tick kwargs
# #TODO catch exception for outer list or first dimension as 1, e.g. squeeze
# #TODO allow legends to be added

# # def barscatter(data_in, transpose = False,
# #                 groupwidth = .75,
# #                 barwidth = .8,
# #                 paired = False,
# #                 unequal = False,
# #                 spaced = False,
# #                 yspace = 20,
# #                 xspace = 0.1,
# #                 barfacecolor_option = 'same', # other options 'between' or 'individual'
# #                 barfacecolor = ['white'],
# #                 baredgecolor_option = 'same',
# #                 baredgecolor = ['black'],
# #                 baralpha = 1,
# #                 scatterfacecolor_option = 'same',
# #                 scatterfacecolor = ['white'],
# #                 scatteredgecolor_option = 'same',
# #                 scatteredgecolor = ['grey'],
# #                 scatterlinecolor = 'grey', # Don't put this value in a list
# #                 scattersize = 80,
# #                 scatteralpha = 1,
# #                 spreadscatters = False,
# #                 linewidth=0.75,
# #                 xlim=[],
# #                 ylim=[],
# #                 ylabel = 'none',
# #                 xlabel = 'none',
# #                 grouplabel = [],
# #                 itemlabel = 'none',
# #                 barlabels = [],
# #                 barlabeloffset=0.025,
# #                 grouplabeloffset=0,
# #                 yaxisparams = 'auto',
# #                 show_legend = 'none',
# #                 legendloc='upper right',
# #                 xfontsize=8,
# #                 ax=[]):
# #     """
# #     Creates a bar graph with data points shown as overlaid circles.
    
# #     Parameters
# #     -------------
# #     data : List, lists of lists or array
# #         Data to be plotted. Will try to convert if needed.
# #     barwidth : Float, optional
# #         Width of bars. Default is 0.9.
# #     paired : Bool, optional
# #         Attempts to add lines between paired data points. Requires number in each group to be matched. Default is False.
# #     unequal : Bool, optional
# #         To be set to True if groups are unequal. Default is False.
# #     spaced : Bool, optional
# #         Spaces out data points so that they are not at an identical x value, e.g. grape bunch style. Default is False.
# #     yspace : Int or Float, optional
# #         Used in conjunction with spaced to determine spacing of data points. Default is 20.
# #     xspace : Float, optional
# #         Used in conjunction with spaced to determine spacing of data points. Default is 0.1.
# #     barfacecolor_option : Str, optional
# #         Chooses bar color option. Default is 'same' and other options are 'between' or 'individual'.
# #     barfacecolor : List of str, optional
# #         If 'between' or 'individual' is chosen for above option then number of colors needs to match number of bars or groups. Default is ['white'].
# #     baredgecolor_option : Str, optional
# #         Chooses bar edge option. Default is 'same', see notes on barfacecolor_option.
# #     baredgecolor : List of str, optional
# #         Bar edge colors. Default is ['black'], see notes on barfacecolor.
# #     baralpha : Float, optional
# #         Sets opacity of bars so must be between 0 and 1. Default is 1.
# #     scatterfacecolor_option : Str, optional
# #         Chooses scatter face option. Default is 'same', see notes on barfacecolor_option.
# #     scatterfacecolor : List of str, optional
# #         Scatter face colors. Default = ['white'], see notes on barfacecolor.
# #     scatteredgecolor_option : Str, optional
# #         Chooses scatter edge option. Default is 'same', see notes on barfacecolor_option.
# #     scatteredgecolor : List of str, optional
# #         Scatter face colors. Default is ['grey'], see notes on barfacecolor.
# #     scatterlinecolor : Str, optional
# #         Color of lines connecting related data points, should not be in a list. Default is 'grey'.
# #     scattersize : Int or Float, optional
# #         Size of datapoints. Default is 80.
# #     scatteralpha : Float, optional
# #         Sets opacity/transparency of scatter points. Default is 1.
# #     spreadscatters : Bool, optional
# #         Not currently functional. Needs to be checked.
# #     linewidth : Float, optional
# #         Width of lines. Default is 0.75.
# #     xlim : List or 2-tuple of floats, optional
# #         Sets limits of x-axis. Default is [].
# #     ylim : List or 2-tuple of floats, optional
# #         Sets limits of x-axis. Default is [].
# #     ylabel : Str, optional
# #         Sets y-axis label. Default is 'none'.
# #     xlabel : Str, optional
# #         Sets x-axis label. Default is 'none'.
# #     grouplabel : List of str, optional
# #         Sets labels for each group. Default is 'auto'.
# #     itemlabel : List of str, optional
# #         Not currently functional. Needs to be checked. Default is 'none'.
# #     barlabels : List of str, optional
# #         Sets labels for each bar. Default is [].
# #     barlabeloffset : Float, optional
# #         Sets barlabel offset relative to x baseline. Default is 0.025.
# #     grouplabeloffset : Float, optional
# #         Sets grouplabel offset relative to x baseline. Default is 0.0250.
# #     yaxisparams : None, optional
# #         Not currently functional. Needs to be checked.
# #     show_legend : Bool or str, optional
# #         Shows legend. Default is 'none'.
# #     legendloc : Str, optional
# #         Sets legend location. Default is 'upper right'.
# #     xfontsize : Int, optional
# #         Sets x-axis font size. Default is 8.
# #     ax : Matplotlib axis object, optional
# #         Axis object to plot in. If not provided, plots in new figure/axis. Default is [].
    
# #     Returns
# #     -------------
# #     ax : Matplotlib axis object
# #         Axis object of plot.
# #     barx : List of floats
# #         x-values where each bar is plotted.
# #     barlist : List of bar container objects
# #         Allows modifcation, e.g. changing of colors of individual bars. See notes.
# #     sclist : List of scatter container objects
# #         Allows modifcation as described above. See notes.
# #     """


    

    


# #     # X ticks
# #     ax.tick_params(
# #         axis='x',          # changes apply to the x-axis
# #         which='both',      # both major and minor ticks are affected
# #         bottom=False,      # ticks along the bottom edge are off
# #         top=False,
# #         labelbottom=False) # labels along the bottom edge are off
    
# #     ax.set_xticks([])






    
    
    
#     return ax, barx, barlist, sclist
      
if __name__ == "__main__":
    print("Updated version")
    # barscatter([[1, 2, 3, 4], [5, 6, 7, 8]], scatteralpha=0.2, paired=True)