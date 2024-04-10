from trompy.barscatter import barscatter # ,  prep_data, data2obj1D, data2obj2D, xyspacer
from trompy.medfilereader import medfilereader, medfilereader_licks, isnumeric, checknsessions, tstamp_to_tdate
from trompy.metafile_utils import metafilereader
from trompy.snipper_utils import processdata, snipper, mastersnipper, zscore, findnoise, removenoise, med_abs_dev, makerandomevents, time2samples, event2sample, resample_snips
from trompy.general_utils import remcheck, random_array, getuserhome, flatten_list, discrete2continuous, findpercentilevalue, logical_subset, find_overlap, download_data
from trompy.lick_utils import lickCalc
from trompy.stats_utils import sidakcorr, mean_and_sem, bonferroni_corrected_ttest, lsd_pval
from trompy.fig_utils import setsameaxislimits, invisible_axes, shadedError, ax2prop, lighten_color, get_violinstats
from trompy.lick_figs import licklengthFig, iliFig, burstlengthFig, ibiFig, burstprobFig, sessionlicksFig
from trompy.trials_figs import trialsFig, trialsMultFig, trialsShadedFig, trialsMultShadedFig, trialstiledFig, makeheatmap
from trompy.roc_utils import rocN, rocshuf, nanroc, run_roc_comparison, plot_ROC_and_line
from trompy.merge_fed_files import merge_files, parse_args
from trompy.lickcalc import Lickcalc, weib_davis, fit_weibull