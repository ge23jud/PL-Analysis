#from idlelib.format import reformat_comment

# Import modules
import numpy as np
import matplotlib.pyplot as plt
#from PIL.ImageChops import constant
from scipy.optimize import curve_fit
#import pandas as pd

# Import from other files
from helper_functions import HelperFunctions

SampleOverview_dir = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\Sample Overview.xlsx"

class DataHandler():

    def load_origin(self, filepath):
        """
        Load data from a .origin file.

        Parameters:
        filepath (str): Path to the .origin file

        Returns:
        tuple: (header_dict, X, Y) where:
            - header_dict: Dictionary with header information
            - X: numpy array with Energy values (eV)
            - Y: numpy array with Powerspectrum values (Counts/time)
        """
        print("Note: Center Wavelength is not included in measurement info due to missing colon in files. Ignore if already fixed")

        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Initialize variables
        header_dict = {}
        header_stop_idx = 9 # first line after header
        data_start_idx = 14

        # Parse header information
        for i, line in enumerate(lines):

            if i == header_stop_idx:
                break

            line = line.strip()

            if not line or line.startswith("(") or line.startswith("Energy"):
                continue # Skip empty lines or line which contain units
            else:
                parts = line.split(':', 1)  # Split line at first colon

            if len(parts) != 2:
                print(f"Error during loading of data. Number other than two columns found in line {i}")
                continue
            else:
                key = parts[0].strip()
                value = parts[1].strip()
                header_dict[key] = value

        energy_values = []
        powerspectrum_values = []

        for line in lines[data_start_idx:]:
            line = line.strip()
            if not line:
                continue

            # Parse data lines (tab or space separated)
            parts = line.split()
            if len(parts) >= 2:
                try:
                    energy = float(parts[0])
                    power = float(parts[1])
                    energy_values.append(energy)
                    powerspectrum_values.append(power)
                except ValueError:
                    continue  # Skip lines that can't be parsed as numbers

        # Convert to numpy arrays
        X = np.array(energy_values)
        Y = np.array(powerspectrum_values)

        return header_dict, X, Y



class Measurement:
    # Parent class for any type of single measurement curve
    # All specific measurement classes e.g. spectrum inherit from this class

    def __init__(self, filepath):

        # Info extracted from filepath
        self.filepath = filepath
        self.spl, self.epi, self.nw = HelperFunctions().get_info_from_filepath(filepath)

        # Info extracted from file itself
        if self.filepath[-6:] == "origin":
            self.info, self.X, self.Y = DataHandler().load_origin(filepath)
        else:
            print("Filetype other than .origin found. Loading this type of data not yet implemented.")


    def display(self):
        print("location: ", self.filepath)
        print("spl-number: ", self.spl)
        print("Epi-number: ", self.epi)
        print("NW: ", self.nw)
        for key in self.info.keys():
            print(key, self.info[key])


class Spectrum(Measurement):

    def __init__(self, filepath):
        super().__init__(filepath)
        self.energy = self.X
        self.wavelength = HelperFunctions().nm_to_ev(self.energy)


class FitFunctions():

    def gaussian(self, x, a, x0, sigma, offset):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + offset


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

class Fitter():

    def __init__(self, f, xdata, ydata, p0=None, error=None, fitrange=[None, None]):
        """
        Tool for simple fits to experimental data

        Parameters:
        f (func): Fit function which takes p+1 arguments (1 independent variable, p parameters)
        xdata (array (n)): x-values of data
        ydata (array (n)): y-values of data
        * p0: initial guess for parameters / default: None
            - tuple (p): Direct specification of initial guesses
            - func: Function to autogenerate initial guesses
            - None: For running fit without initial guesses
        * errors (array (n)): y-errors of data
        * fitrange: Range of x-data to use for fit / default: [None, None]
            - list (2): Boundary indices of fit range; If None, no boundary is set
            - func: Function that returns boundary indices, e.g. by span selection

        Returns:
        ?
        """
        self.f = f
        self.X, self.Y, self.error = xdata, ydata, error
        if callable(fitrange):
            self.fitrange = fitrange(self.X, self.Y)
        else:
            self.fitrange = fitrange
        self.X_fit, self.Y_fit = self.X[self.fitrange[0]:self.fitrange[1]], self.Y[self.fitrange[0]:self.fitrange[1]]
        if self.error is not None:
            self.error_fit = self.error[fitrange[0]:fitrange[1]]
        else:
            self.error_fit = self.error

        if callable(p0):
            self.p0 = p0(self.X_fit, self.Y_fit)
        else:
            self.p0 = p0

        self.opt, self.cov = self.fit()

    # def set_fitrange(self, fitrange):
    #     """
    #     Change self.X_fit, self.Y_fita and self.error_fit.
    #
    #     Parameters:
    #     Returns:
    #     tuple: (a, x0 , sigma , offset) -> Initial guesses for amplitude, peak position, peak width and offset
    #     """

    def fit(self):
        """
        Perform scipy.curve_fit on self.X_fit and self.Y_fit.

        Returns:
        tuple (p), array (p, p): optimized fit parameters, covariance matrix
        """
        opt, cov = curve_fit(self.f, self.X_fit, self.Y_fit, self.p0, self.error_fit)
        return opt, cov



# Taken from Claude, might need optimization at some point
class SpanSelector():

    def select_x_span(self, xdata, ydata, title="Select X-Span"):
        """
        Plot x,y data and allow interactive selection of x-span.

        Parameters:
        xdata (np-array)
        ydata (np-array)
        title (str): Text to display on the prompt

        Returns:
        tuple : (start_idx, end_idx) First and last indices of x-data within selected range
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y, 'b-', linewidth=1)
        ax.set_title(f"{title}\nClick and drag to select range, then press Enter or close plot")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)

        # Variables to store selection
        selection = {'x1': None, 'x2': None, 'active': False}
        span_line = None

        def on_press(event):
            if event.inaxes == ax and event.button == 1:  # Left mouse button
                selection['x1'] = event.xdata
                selection['active'] = True

        def on_motion(event):
            nonlocal span_line
            if selection['active'] and event.inaxes == ax:
                selection['x2'] = event.xdata

                # Remove previous span visualization
                if span_line is not None:
                    span_line.remove()

                # Draw current selection
                x1, x2 = sorted([selection['x1'], selection['x2']])
                span_line = ax.axvspan(x1, x2, alpha=0.3, color='red',
                                       label=f'Selected: [{x1:.3f}, {x2:.3f}]')
                ax.legend()
                fig.canvas.draw()

        def on_release(event):
            if selection['active'] and event.inaxes == ax:
                selection['x2'] = event.xdata
                selection['active'] = False

        def on_key(event):
            if event.key == 'enter':
                plt.close(fig)

        # Connect event handlers
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('key_press_event', on_key)

        plt.show()

        # Process selection
        if selection['x1'] is not None and selection['x2'] is not None:
            x_min, x_max = sorted([selection['x1'], selection['x2']])

            # Find indices
            start_idx = np.argmax(x >= x_min)
            end_idx = len(x) - 1 - np.argmax(x[::-1] <= x_max)

            print(f"Selected range: [{x_min:.3f}, {x_max:.3f}]")
            print(f"Indices: [{start_idx}, {end_idx}]")
            print(f"Data points in range: {end_idx - start_idx + 1}")

            return start_idx, end_idx
        else:
            print("No selection made")
            return None, None



# class Analysis():





# path = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\20250715-plm0001_spl2411_spl2407_spl2415_spl2505\250716_Epi-1839_NW3-7_Epi-1888_NW1-5\Epi-1839_NW4-7\darkcounts_0.9eV_10s_PS__000.origin"
# x = Measurement(path)


x = np.linspace(0, 100, 1000)
y = np.sin(x)
#
# fit = SpanSelector()
# fit.select_x_span(x, y)

x = np.array([-1.98, -1.74, -1.51, -1.27, -1.04, -0.80, -0.57, -0.33, -0.10, 0.14, 0.37, 0.61, 0.84, 1.08, 1.31, 1.55, 1.78, 2.02, 2.25, 2.49, 2.72, 2.96, 3.19, 3.43, 3.66, 3.90, 4.13, 4.37, 4.60, 4.84, 5.07, 5.31, 5.54, 5.78, 6.01, 6.25, 6.48, 6.72, 6.95, 7.19, 7.42, 7.66, 7.89, 8.13, 8.36, 8.60, 8.83, 9.07, 9.30, 9.54])
y = np.array([6.2, 4.8, 9.1, 4.2, 7.6, 3.9, 5.9, 8.4, 3.3, 7.1, 4.1, 6.8, 2.8, 5.6, 7.9, 3.6, 5.7, 2.3, 6.3, 8.0, 4.2, 12.5, 7.1, 15.3, 26.8, 42.5, 65.3, 78.9, 89.2, 82.7, 91.5, 75.9, 58.4, 42.1, 31.6, 26.8, 19.5, 15.2, 12.7, 10.4, 9.9, 11.2, 7.5, 12.1, 8.2, 10.7, 6.8, 9.0, 11.4, 7.3])
fit = Fitter(FitFunctions().gaussian, x, y, fitrange=SpanSelector().select_x_span, p0=InitialGuessGenerator().create_initial_guess_single_peak)

print(fit.opt)

# plt.plot(x, y)
# plt.plot(x, FitFunctions().gaussian(x, *[82.67009058,  4.84584268,  0.71605576,  8.97632381]))
# plt.show()