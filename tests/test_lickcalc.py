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

    #testing if ocrrect number of bursts identified
    lc = Lickcalc(licks=licks)
    assert lc.burst_number == 11

    # testing if min_burst_length works
    lc = Lickcalc(licks=licks, min_burst_length=5)
    assert lc.burst_number == 8

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
    


# if __name__ == '__main__':
#     unittest.main()

# class TestLickCalc(unittest.TestCase):
#     def setUp(self):
#         self.licks = [0.1, 0.2, 0.3, 0.4, 0.5]
#         self.offset = [0.1, 0.2, 0.3, 0.4, 0.5]
#         self.kwargs = {
#             'longlick_threshold': 0.3,
#             'burst_threshold': 0.5,
#             'min_burst_length': 1,
#             'run_threshold': 10,
#             'min_run_length': 1,
#             'binsize': 60,
#             'hist_density': False,
#             'ignorelongilis': False,
#             'licks': self.licks,
#             'offset': self.offset
#         }

#     def test_init(self):
#         lc = LickCalc(**self.kwargs)
#         self.assertEqual(lc.longlick_threshold, 0.3)
#         self.assertEqual(lc.burst_threshold, 0.5)
#         self.assertEqual(lc.min_burst_length, 1)
#         self.assertEqual(lc.run_threshold, 10)
#         self.assertEqual(lc.min_run_length, 1)
#         self.assertEqual(lc.binsize, 60)
#         self.assertEqual(lc.hist_density, False)
#         self.assertEqual(lc.ignorelongilis, False)
#         np.testing.assert_array_equal(lc.licks, np.array(self.licks))
#         np.testing.assert_array_equal(lc.offset, np.array(self.offset))
#         self.assertIsNone(lc.licklength)
#         self.assertIsNone(lc.longlicks)
#         np.testing.assert_array_equal(lc.ilis, np.array([0.1, 0.1, 0.1, 0.1]))
#         self.assertEqual(lc.total, 5)

#     def test_get_burst_inds(self):
#         lc = LickCalc(**self.kwargs)
#         burst_inds = lc.get_burst_inds()
#         expected_burst_inds = [3, 4]
#         np.testing.assert_array_equal(burst_inds, np.array(expected_burst_inds))

#     # Add more test methods for other functions...

