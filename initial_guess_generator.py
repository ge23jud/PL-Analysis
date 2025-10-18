import numpy as np
from PIL.ImageChops import offset
from scipy.constants import sigma


class InitialGuessGenerator():

    def single_gaussian_const_bg(self, xdata, ydata):
        """
        Create an initial guess for a single gaussian fit.

        Returns:
        tuple: (a, x0 , sigma , offset) -> Initial guesses for amplitude, peak position, peak width and offset
        """
        # Approximate offset based on average of first and last value of fit range
        offset = 0.5 * (ydata[0] + ydata[-1])

        # Approximate amplitude based on maximum value within fit range
        a_idx = np.argmax(ydata)
        a = ydata[a_idx] + offset

        # Print warning, when data maximum is found at the edges of the fit range (potentially, maximum is not peak)
        if a_idx/len(xdata) < 0.1 or a_idx/len(xdata) > 0.9:
            print("Initial guess warning: Maximum of data was detected far away from the center of the fit range!")

        # Approximate peak position based on x-value of maximum value within fit range
        x0 = xdata[a_idx]

        # Approximate FWHM based on position of value which first exceeds half of maximum value when iteration over values
        for x, y in zip(xdata, ydata):
            if y >= a / 2:
                sigma = (x0 - x) / np.sqrt(2 * np.log(2))  # FWHM = 2 * (x0-x); sigma = FWHM/(2*sqrt(2*ln2))
                break

        return a, x0, sigma, offset


    def single_gaussian_linear_bg(self, xdata, ydata):

        a, x0, sigma, offset = self.single_gaussian_const_bg(xdata, ydata)

        m = (ydata[-1] - ydata[0])/(xdata[-1] - xdata[0])
        t = ydata[0] - m * xdata[0]

        return a, x0, sigma, m, t
