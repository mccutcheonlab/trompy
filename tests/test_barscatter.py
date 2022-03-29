# %%
"""
Created on Tue Mar 29 2022

@author: jmc010
"""
import pytest
import numpy as np
import trompy as tp
import matplotlib.pyplot as plt

%matplotlib inline

np.random.seed(222)

def test_alpha():
    tp.barscatter([[1, 2, 3, 4], [5, 6, 7, 8]], scatteralpha=0.2, paired=True)

if __name__ == "__main__":
    test_alpha()
# %%
