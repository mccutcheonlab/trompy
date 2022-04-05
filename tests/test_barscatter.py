# %%
"""
Created on Tue Mar 29 2022

@author: jmc010
"""
import pytest
import numpy as np
import trompy as tp
import matplotlib.pyplot as plt

#%matplotlib inline

np.random.seed(222)

def make_data(n, dtype="int"):
    if dtype == "int":
        return np.random.randint(10, size=n)
    else:
        return np.random.random(n)

# def test_unequal_groups():
    
#     data_in = [[np.random.randint(10, size=3), np.random.randint(10, size=4), np.random.randint(10, size=2)], \
#          [np.random.randint(10, size=5), np.random.randint(10, size=6), np.random.randint(10, size=2)]]
    
#     output = tp.barscatter(data_in, linewidth=4, bar_kwargs={"yerr": 2}, ax_kwargs={"ylabel": "hey"}, xlabel="woo", ylim=(0,20),
#     grouplabel=["nr", "pr"], barlabels=["bar"]*6,
#     show_legend=True)

# def test_alpha():
#     output = tp.barscatter([[1, 2, 3, 4], [5, 6, 7, 8]], scatteralpha=0.2, paired=True)

# def test_prep_data():

#     data_in = [[np.random.randint(10, size=3), np.random.randint(10, size=4), np.random.randint(10, size=2)], \
#          [np.random.randint(10, size=5), np.random.randint(10, size=6)]]

def test_improper_structures():
    
    # # unbalanced, grouped
    data_in = [[np.random.randint(10, size=3), np.random.randint(10, size=4), np.random.randint(10, size=2)], \
         [np.random.randint(10, size=5), np.random.randint(10, size=6)]]
    with pytest.raises(ValueError):
        tp.barscatter(data_in)

    data_in = data_in = [make_data(9), make_data(8), "hey there", make_data(7), make_data(5)]
    with pytest.raises(TypeError):
        tp.barscatter(data_in)

def test_different_working_structures():
    # one bar
    data_in = [make_data(9)]
    tp.barscatter(data_in)

    # # five bars, 1D, unbalanced
    data_in = [make_data(9), make_data(8), make_data(3), make_data(7), make_data(5)]
    tp.barscatter(data_in, scatteroffset=-0.5)
    
    # # five bars, 1D, balanced
    data_in = [make_data(9), make_data(9), make_data(9), make_data(9), make_data(9)]
    tp.barscatter(data_in)

    # grouped, 2x2, unbalanced
    data_in = [[make_data(9), make_data(9)], [make_data(9), make_data(9)]]
    tp.barscatter(data_in)
    tp.barscatter(data_in, paired=True)

    # grouped, 2x2, unbalanced
    data_in = [[make_data(9), make_data(9)], [make_data(8), make_data(8)]]
    tp.barscatter(data_in)
    tp.barscatter(data_in, paired=True)
    
    # grouped, 2x4, balanced
    tmplist = list(make_data(9))
    data_in = [[tmplist, tmplist, tmplist, tmplist], [tmplist, tmplist, tmplist, tmplist]]
    tp.barscatter(data_in)
    tp.barscatter(data_in, paired=True)

    # grouped, 2x4, unbalanced
    tmplist2 = list(make_data(7))
    data_in = [[tmplist, tmplist, tmplist, tmplist], [tmplist2, tmplist2, tmplist2, tmplist2]]
    tp.barscatter(data_in)
    tp.barscatter(data_in, paired=True, errorbars=True, scatteroffset=0.9)


if __name__ == "__main__":
    # test_alpha()
    # test_unequal_groups()
    # test_prep_data()
    test_improper_structures()
    # test_different_structures()


# %%

# %%
