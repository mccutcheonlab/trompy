from trompy.barscatter import barscatter, setcolors, data2obj1D, data2obj2D, xyspacer
from trompy.medfilereader import medfilereader, isnumeric
from trompy.metafile_utils import metafilemaker, metafilereader
from trompy.snipper_utils import snipper, mastersnipper, zscore, findnoise, removenoise, med_abs_dev, makerandomevents, time2samples, event2sample
from general_utils import remcheck, random_array
from lick_utils import lickCalc, removeshortbursts, calculate_burst_prob, weib_davis, fit_weibull