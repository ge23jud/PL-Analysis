import numpy as np
import matplotlib.pyplot as ptl
from scipy.optimize import curve_fit

class Measurement:
    # Parent class for any type of single measurement curve
    # All specific measurement classes e.g. spectrum inherit from this class

    def __init__(self, filepath):
        self.filepath = filepath

        ## Info ##
        # Any type of information other than x- and y-data
        # self.info =

        ## Data ##
        self.X = 5
        self.Y = 6


class Spectrum(Measurement):

    def __init__(self, filepath):
        super().__init__(filepath)
        self.X += 1

    def show(self):
        print(self.X)


testclass = Spectrum(1)
testclass.show()







