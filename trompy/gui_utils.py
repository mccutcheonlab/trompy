# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 13:03:34 2020

@author: admin
"""
from tkinter import filedialog
from tkinter import messagebox
import os

def get_location():
    loc = filedialog.askdirectory(initialdir=os.getcwd(), title='Select a save folder.')
    os.chdir(loc)
    return loc
       
def alert(msg):
    print(msg)
    messagebox.showinfo('Error', msg)