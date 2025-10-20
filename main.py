# Import modules
import os.path

import matplotlib.pyplot as plt
import numpy as np

# Import from other files
from fitter import Fitter
from interactor import Interactor
from initial_guess_generator import InitialGuessGenerator
from fit_functions import FitFunctions
from measurement import Measurement, Spectrum, DarkSpectrum, PowerCalibration, PowerSeries
from data_handler import DataHandler
from helper_functions import HelperFunctions
from plot import Plot

SampleOverview_dir = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\Sample Overview.xlsx"

path = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\13_PL\20250822-plm0001_spl2525_spl2409\spl2409_Epi-1780\NW11\right\EPI-1780_NW11_1.3eV_0.2s_10K__000.origin"



spec = PowerSeries(DataHandler().load_series_origin, path)
intervals = spec.select_fit_intervals()
f = FitFunctions().single_gaussian_linear_bg
p0 = InitialGuessGenerator().single_gaussian_linear_bg

spec.fit_peaks(intervals, f, p0)
## To do ##

# Implement MeasurementSeries()
# Make NW-number optional

# Shortcuts
# Str+B on method call: Jump to implementation
# Shift+F6 while method marked: rename method everywhere
# Str+W: Inside out selection
# Str+N: Class search
# Str+Shift+F: Everywhere search
# Str+Shift+A: Everything search