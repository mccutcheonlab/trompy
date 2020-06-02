# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 15:56:36 2020

@author: admin
"""
import numpy as np
from trompy import *
import tdt

import matplotlib.pyplot as plt

import sys
from tkinter import *

folder = "C:\\Test Data\\data\\FiPho-180416\\"

tmp = tdt.read_block(folder)

data = tmp.streams._4654.data
fs = tmp.streams._4654.fs
events = tmp.epocs.PtAB.onset

ptab = tmp.epocs.PtAB

# randevents = list(np.sort(np.random.randint(low=120, high=int(len(data)/fs)-120, size=50)))
# def search_for_events(tank):
#     tmp = tdt.read_block(tank)
    
    
    
    
#     for key in tmp.keys():
#         print(key)
        
#         try:
#             search_within(tmp[key])
#         except AttributeError:
#             print(np.shape((tmp[key])))
            
#         # try:
#         #     if tmp.key()
#         # search_within()
    
# def search_within(struct):
#     for attrib in struct.__dict__.keys():
#         print(attrib)
    

# search_for_events(folder)
    
    

# def nestedvalues1(key):
#     filemenu2 = Menu(filemenu)
#     filemenu2.add_cascade(label=key, menu=filemenu2)

# def comingsoon(key):
#     print(key, 'coming soon')
    
# def searchstructure()

# root = Tk(  )

# # Insert a menu bar on the main window
# eventmenu = Menu(root)
# root.config(menu=eventmenu)

# findmenu = Menu(eventmenu)
# eventmenu.add_cascade(label='Find', menu=findmenu)

# structmenu = Menu(findmenu)
# for key in tmp.keys():
#     findmenu.add_command(label=key)
    


# findmenu.add_cascade()

# for key in tmp.keys():
#     filemenu.add_command(label=key, command=nestedvalues1(key))

# root.mainloop(  )


# snips = mastersnipper(data, data, data, fs, events,
#                       snipfs=10, trialLength=30, preTrial=10,
#                       hullabaloo='trig')

# print(np.shape(snips['blue']))
# avg = np.mean(snips['blue'], axis=0)

# fig, ax = plt.subplots()
# ax.plot(np.mean(snips['blue'], axis=0))
# plt.show()