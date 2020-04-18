# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:22:10 2020

@author: admin
"""
import matplotlib.pyplot as plt
import numpy as np

def licklengthFig(ax, data, contents = '', color='grey'):          
    if len(data['longlicks']) > 0:
        longlicklabel = str(len(data['longlicks'])) + ' long licks,\n' +'max = ' + '%.2f' % max(data['longlicks']) + ' s.'        
    else:
        longlicklabel = 'No long licks.'
    
    figlabel = str(len(data['licklength'])) + ' total licks.\n' + longlicklabel

    ax.hist(data['licklength'], np.arange(0, 0.3, 0.01), color=color)
    ax.text(0.9, 0.9, figlabel, ha='right', va='top', transform = ax.transAxes)
    ax.set_xlabel('Lick length (s)')
    ax.set_ylabel('Frequency')
    ax.set_title(contents)
    
def iliFig(ax, data, contents = '', color='grey'):
    ax.hist(data['ilis'], np.arange(0, 0.5, 0.02), color=color)
    
    figlabel = '%.2f Hz' % data['freq']
    ax.text(0.9, 0.9, figlabel, ha='right', va='top', transform = ax.transAxes)
    
    ax.set_xlabel('Interlick interval (s)')
    ax.set_ylabel('Frequency')
    ax.set_title(contents)
    
def burstlengthFig(ax, data, contents='', color3rdbar=False):
    
    figlabel = (str(data['bNum']) + ' total bursts\n' +
                str('%.2f' % data['bMean']) + ' licks/burst.')
                                                
    n, bins, patches = ax.hist(data['bLicks'], range(0, 20), normed=1)
    ax.set_xticks(range(1,20))
    ax.set_xlabel('Licks per burst')
    ax.set_ylabel('Frequency')
    ax.set_xticks([1,2,3,4,5,10,15])
#        ax.text(0.9, 0.9, figlabel1, ha='right', va='center', transform = ax.transAxes)
    ax.text(0.9, 0.8, figlabel, ha='right', va='center', transform = ax.transAxes)
    
    if color3rdbar == True:
        patches[3].set_fc('r')
    
def ibiFig(ax, data, contents = ''):
    ax.hist(data['bILIs'], range(0, 20), normed=1)
    ax.set_xlabel('Interburst intervals')
    ax.set_ylabel('Frequency')
    
def burstprobFig(ax, data):
    
#    figlabel = '{:d} total bursts\n{:.2f} licks/burst'.format(
#            data['bNum'], data['bMean'])
    x=data['burstprob'][0]
    y=data['burstprob'][1]
    alpha=data['weib_alpha']
    beta=data['weib_beta']
    rsq=data['weib_rsq']
#    x, y = calculate_burst_prob(data['bLicks'])
    ax.scatter(x,y,color='none', edgecolors='grey')
    
#    alpha, beta, r_squared = fit_weibull(x, y)
    ax.plot(x, weib_davis(x, alpha, beta), c='orange')
          
    figlabel = 'Fitted values:\nalpha={:.2f}\nbeta={:.2f}\nrsq={:.2f}'.format(
            alpha, beta, rsq)

    ax.set_xlabel('Burst size (n)')
    ax.set_ylabel('Probability of burst>n')
    ax.text(0.9, 0.9, figlabel, ha='right', va='top', transform = ax.transAxes)
    
#    return {'alpha': alpha, 'beta': beta, 'rsq': r_squared}
    
def sessionlicksFig(ax, licks):
    ax.hist(licks, range(0,3600,60), color='grey', alpha=0.4)
    yraster = [ax.get_ylim()[1]] * len(licks)
    ax.scatter(licks, yraster, s=50, facecolors='none', edgecolors='grey')

    ax.set_xticks(np.multiply([0, 10, 20, 30, 40, 50, 60],60))
    ax.set_xticklabels(['0', '10', '20', '30', '40', '50', '60'])
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Licks per min')