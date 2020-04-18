from trompy.barscatter import barscatter, setcolors, data2obj1D, data2obj2D, xyspacer
from trompy.medfilereader import medfilereader, isnumeric
from trompy.metafile_utils import metafilemaker, metafilereader
from trompy.snipper_utils import snipper, mastersnipper, zscore, findnoise, removenoise, med_abs_dev, makerandomevents, time2samples, event2sample
from trompy.general_utils import remcheck, random_array, getuserhome, flatten_list, discrete2continuous, findpercentilevalue
from trompy.lick_utils import lickCalc, removeshortbursts, calculate_burst_prob, weib_davis, fit_weibull
from trompy.stats_utils import sidakcorr, mean_and_sem, bonferroni_corrected_ttest
from trompy.fig_utils import setsameaxislimits, invisible_axes, shadedError, ax2prop, lighten_color, get_violinstats
from trompy.lick_figs import licklengthFig, iliFig, burstlengthFig, ibiFig, burstprobFig, sessionlicksFig
from trompy.trials_figs import trialsFig, trialsMultFig, trialsShadedFig, trialsMultShadedFig, trialstiledFig
from trompy.lick_gui import Window, get_location, alert, checknsessions, medfilereader_licks, tstamp_to_tdate, start_gui