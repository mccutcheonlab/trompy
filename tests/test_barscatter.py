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

def make_data_array():
    data_array={}
    data_array["one bar"] = [make_data(9)]
    data_array["5x1, balanced"] = [make_data(9), make_data(9), make_data(9), make_data(9), make_data(9)]
    data_array["5x1, unbalanced"] = [make_data(9), make_data(8), make_data(3), make_data(7), make_data(5)]
    data_array["2x2, balanced"] = [[make_data(9), make_data(9)], [make_data(9), make_data(9)]]
    data_array["2x2, unbalanced"] = [[make_data(9), make_data(9)], [make_data(8), make_data(8)]]
    
    tmplist = list(make_data(9))
    tmplist2 = list(make_data(7))

    data_array["2x4, balanced"] = [[tmplist, tmplist, tmplist, tmplist], [tmplist, tmplist, tmplist, tmplist]]
    data_array["2x4, unbalanced"] = [[tmplist, tmplist, tmplist, tmplist], [tmplist2, tmplist2, tmplist2, tmplist2]]

    return data_array


def test_alpha():
    output = tp.barscatter([[1, 2, 3, 4], [5, 6, 7, 8]], scatteralpha=0.2, paired=True)


def check_colors(data_in, n_colors):
    colors = [(1.0, 0.0, 0.0, 1), (0.0, 1.0, 0.0, 1), (0.0, 0.0, 1.0, 1),
              (0.0, 1.0, 1.0, 1), (1.0, 0.0, 1.0, 1)]*2
    colors_in = colors[:n_colors]
    _, _, bars, _ = tp.barscatter(data_in, barfacecolor_option="individual", barfacecolor = colors_in)

    colors_out = []
    for bar in bars:
        colors_out.append(bar.get_children()[0].get_facecolor())

    return colors_in == colors_out

def test_many_colors():
    data_array = make_data_array()

    N_COLORS=[1, 5, 5, 4, 4, 8, 8]
    for key, n_colors in zip(data_array, N_COLORS):
        assert check_colors(data_array[key], n_colors)

def test_kwargs():
    data_in = [make_data(10)]
    tp.barscatter(data_in, errorbars=True, error_bars=False)

def test_improper_structures():
    
    # # unbalanced, grouped
    data_in = [[np.random.randint(10, size=3), np.random.randint(10, size=4), np.random.randint(10, size=2)], \
         [np.random.randint(10, size=5), np.random.randint(10, size=6)]]
    with pytest.raises(ValueError):
        tp.barscatter(data_in)

    data_in = data_in = [make_data(9), make_data(8), "hey there", make_data(7), make_data(5)]
    with pytest.raises(TypeError):
        tp.barscatter(data_in)

def test_spaced():
    data_in = [make_data(3)]
    tp.barscatter(data_in, spaced=True)

def test_different_working_structures():
    data_array = make_data_array()

    tp.barscatter(data_array["one bar"])
    tp.barscatter(data_array["5x1, unbalanced"])
    tp.barscatter(data_array["5x1, unbalanced"])
    tp.barscatter(data_array["2x2, balanced"])
    tp.barscatter(data_array["2x2, balanced"], paired=True)
    tp.barscatter(data_array["2x2, unbalanced"])
    tp.barscatter(data_array["2x2, unbalanced"], paired=True)
    tp.barscatter(data_array["2x4, balanced"])
    tp.barscatter(data_array["2x4, balanced"], paired=True)
    tp.barscatter(data_array["2x4, unbalanced"])
    tp.barscatter(data_array["2x4, unbalanced"], paired=True)

if __name__ == "__main__":
    # test_alpha()
    # test_improper_structures()
    # test_different_working_structures()
    # test_many_colors()
    # test_kwargs()
    # test_alpha()
    test_spaced()
    



# %%
