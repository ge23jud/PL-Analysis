import numpy as np

class FitFunctions():

    def gaussian(self, x, a, x0, sigma, offset):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + offset
