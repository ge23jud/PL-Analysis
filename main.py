import numpy as np
import matplotlib.pyplot as ptl
from scipy.optimize import curve_fit

class Measurement:
    # Parent class for any type of single measurement curve
    # All specific measurement classes e.g. spectrum inherit from this class

    def __int__(self, filepath):
        self.filepath = filepath

        ## Info ##
        # Any type of information other than x- and y-data
        # self.info =

        ## Data ##
        # self.X =
        # self.Y =




