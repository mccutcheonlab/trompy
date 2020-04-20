# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 13:03:34 2020

@author: admin
"""
from tkinter import filedialog
from tkinter import messagebox

def get_location():
    loc = filedialog.askdirectory(initialdir=currdir, title='Select a save folder.')
    return loc
       
def alert(msg):
    print(msg)
    messagebox.showinfo('Error', msg)