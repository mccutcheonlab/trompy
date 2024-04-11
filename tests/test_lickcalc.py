# %%
import pytest
import unittest
import numpy as np
np.random.seed(1234)
from trompy import Lickcalc

def make_toy_data():
    import numpy as np

    short_ilis = np.random.normal(0.16, 0.05, 100)
    med_ilis = [x for x in np.random.poisson(1.5, 10) if x > 0]
    long_ilis = [x for x in np.random.poisson(30, 3) if x > 0]

    all_ilis = np.concatenate([short_ilis, med_ilis, long_ilis])
    np.random.shuffle(all_ilis)

    timestamps = np.cumsum(all_ilis)

    return timestamps

def test_burstcalc():
    licks = make_toy_data()
    # import matplotlib.pyplot as plt
    # plt.plot(licks)
    # plt.show()

    #testing if correct number of bursts identified
    lc = Lickcalc(licks=licks)
    assert lc.burst_number == 11

    # testing if min_burst_length works
    lc = Lickcalc(licks=licks, min_burst_length=5)
    assert lc.burst_number == 8
    
    print(lc.runs_start)

def test_runcalc():
    licks = make_toy_data()

    # testing if correct number of runs identified
    lc = Lickcalc(licks=licks)
    assert lc.runs_number == 4

def test_longlicks():
    licks = make_toy_data()
    licklengths = np.random.normal(0.06, 0.01, len(licks))
    licklengths[10] = 3
    offsets = licks + licklengths

    # testing if long lick can be identified
    lc = Lickcalc(licks=licks, offset=offsets)
    assert lc.longlicks[0] == 3.0

if __name__ == "__main__":
    test_burstcalc()
    test_runcalc()
    test_longlicks()
    


# %%
