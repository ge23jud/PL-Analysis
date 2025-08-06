import numpy as np

class InitialGuessGenerator():

    def create_initial_guess_single_peak(self, xdata, ydata):
        """
        Create an initial guess for a single peak fit.

        Returns:
        tuple: (a, x0 , sigma , offset) -> Initial guesses for amplitude, peak position, peak width and offset
        """
        # Approximate amplitude based on maximum value within fit range
        a_idx = np.argmax(ydata)
        a = ydata[a_idx]

        # Approximate peak position based on x-value of maximum value within fit range
        x0 = xdata[a_idx]

        # Approximate FWHM based on position of value which first exceeds half of maximum value when iteration over values
        for x, y in zip(xdata, ydata):
            if y >= a / 2:
                sigma = (x0 - x) / np.sqrt(2 * np.log(2))  # FWHM = 2 * (x0-x); sigma = FWHM/(2*sqrt(2*ln2))
                break

        # Approximate offset based on average of first and last value of fit range
        offset = 0.5 * (ydata[0] + ydata[-1])

        return a, x0, sigma, offset
