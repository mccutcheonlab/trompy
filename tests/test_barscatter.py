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

def test_unequal_groups():
    
    data_in = [[np.random.randint(10, size=3), np.random.randint(10, size=4), np.random.randint(10, size=2)], \
         [np.random.randint(10, size=5), np.random.randint(10, size=6), np.random.randint(10, size=2)]]
    
    print(np.shape(data_in))
    
    output = tp.barscatter(data_in)

def test_alpha():
    output = tp.barscatter([[1, 2, 3, 4], [5, 6, 7, 8]], scatteralpha=0.2, paired=True)

def test_prep_data():

    data_in = [[np.random.randint(10, size=3), np.random.randint(10, size=4), np.random.randint(10, size=2)], \
         [np.random.randint(10, size=5), np.random.randint(10, size=6)]]


    dims = np.ndim(data_in)
    print(type(data_in), dims)


    data_out = tp.prep_data(data_in)

    print(data_out.dtype)
    print(data_out[1][0].dtype)
    print(data_out[1][0])

    # shape = np.shape(data_out)
    # data_new = data_out.reshape(shape, )

if __name__ == "__main__":
    # test_alpha()
    test_unequal_groups()
    test_prep_data()
    # print("hey")


# %%

# %%
