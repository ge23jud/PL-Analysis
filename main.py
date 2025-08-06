# Import modules
import numpy as np


# Import from other files
from fitter import Fitter
from span_selector import SpanSelector
from initial_guess_generator import InitialGuessGenerator
from fit_functions import FitFunctions
from measurement import Measurement, Spectrum
from data_handler import DataHandler
from helper_functions import HelperFunctions

SampleOverview_dir = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\Sample Overview.xlsx"



x = np.array([-1.98, -1.74, -1.51, -1.27, -1.04, -0.80, -0.57, -0.33, -0.10, 0.14, 0.37, 0.61, 0.84, 1.08, 1.31, 1.55, 1.78, 2.02, 2.25, 2.49, 2.72, 2.96, 3.19, 3.43, 3.66, 3.90, 4.13, 4.37, 4.60, 4.84, 5.07, 5.31, 5.54, 5.78, 6.01, 6.25, 6.48, 6.72, 6.95, 7.19, 7.42, 7.66, 7.89, 8.13, 8.36, 8.60, 8.83, 9.07, 9.30, 9.54])
y = np.array([6.2, 4.8, 9.1, 4.2, 7.6, 3.9, 5.9, 8.4, 3.3, 7.1, 4.1, 6.8, 2.8, 5.6, 7.9, 3.6, 5.7, 2.3, 6.3, 8.0, 4.2, 12.5, 7.1, 15.3, 26.8, 42.5, 65.3, 78.9, 89.2, 82.7, 91.5, 75.9, 58.4, 42.1, 31.6, 26.8, 19.5, 15.2, 12.7, 10.4, 9.9, 11.2, 7.5, 12.1, 8.2, 10.7, 6.8, 9.0, 11.4, 7.3])
fit = Fitter(FitFunctions().gaussian, x, y, fitrange=SpanSelector().select_x_span, p0=InitialGuessGenerator().create_initial_guess_single_peak)

print(fit.opt)

