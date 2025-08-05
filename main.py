from idlelib.format import reformat_comment

import numpy as np
import matplotlib.pyplot as plt
from PIL.ImageChops import constant
from scipy.optimize import curve_fit
import re
import pandas as pd
from scipy import constants
from scipy.signal import find_peaks

SampleOverview_dir = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\Sample Overview.xlsx"

class HelperFunctions():

    def nm_to_ev(self, input):
        """
        Convert energy to wavelength and vice versa.

        Args:
            input (float/array): wavelength [m] or energy [eV]

        Returns:
            wavelength [m] (float/array) or energy [eV] (float/array)
        """
        return  constants.h * constants.c / constants.e / input

    def reformat_splnumber(self, splnumber):
        """
        Transform spl-number from format splXXXX to format XX-XX.

        Args:
            splnumber (str): spl-number in format splXXXX

        Returns:
            spl-number (str) in format XX-XX
        """
        x1, x2 = splnumber[3:5], splnumber[5:]
        return x1 + "-" + x2

    def get_spl_from_epi(file_path, epinumber):
        """
        Get spl-number from Epi-number.

        Args:
            file_path (str): Path to the Excel file
            epinumber (str): Substring to search for in growth column
            -> format: epiXXXX

        Returns:
            spl-number
        """
        header_text = "Growth"
        df = pd.read_excel(SampleOverview_dir)

        row_epi = None # Find row of passed epi number by looking for epinumber in column

        for idx, value in df[header_text].items():
            if epinumber in str(value):
                row_epi = idx
                break

        if row_epi is None:
            print("Epi number not found.")
            return None  # Epi number not found in column B

        return df.iloc[row_epi, 0]


    def get_epi_from_spl(self, splnumber):
        """
        Get Epi-number from spl-number.

        Args:
            file_path (str): Path to the Excel file
            splnumber (str): Substring to search for in growth or
            -> format: splXXXX

        Returns:
            Epi-number
        """
        splnumber_reformat = HelperFunctions().reformat_splnumber(splnumber)

        header_text_growth, header_text_cleaved, header_text_transfer = "Growth", "Cleaved From", "NW Transfer"
        df = pd.read_excel(SampleOverview_dir)

        row_epi = None

        # Find row of passed spl-number by looking for splnumber_reformat in column "Name" of SampleOverview
        for idx, value in df["Name"].items():
            if splnumber_reformat in str(value):
                row_epi = idx
                break

        if row_epi == None:
            print("Sample not found")
            return

        if not pd.isna(df[header_text_growth][idx]): # If growth column contains value, extract epi number from there
            return df[header_text_growth][idx].split("-")[1].strip() # Get value from cell, extract substring after "-" and strip potential spaces

        # Can either contain transfer from sample or transfer to sample. Only in first case, which is the relevant one, there is the substring "Epi" contained in the cell
        elif not pd.isna(df[header_text_transfer][idx]) and "Epi" in df[header_text_transfer][idx]:
            return "epi" + df[header_text_transfer][idx].split("-")[1][:4] # Get first three chars after "-" (number) and add it to "epi"

        elif not pd.isna(df[header_text_cleaved][idx]):
            # The "Cleaved From" column, again contains the spl-number of the sample, from which was cleaved.
            # Recursively repeat task with this spl-number
            return self.get_epi_from_spl(df[header_text_cleaved][idx])


    def get_info_from_filepath(self, filepath):
        """
        Get spl-number, Epi-number and NW-number from filepath.

        Args:
            file_path (str): Path to the Excel file

        Returns:
            (tuple): spl-number (str), Epi-number (str), NW-number (list of strings)
        """
        filename = filepath.split("\\")[-1]
        filename_split = filename.split("_")

        splnumber, epinumber, nwnumber = None, None, None

        for name in filename_split:
            if "spl" in name:
                splnumber = name
            if "Epi" in name:
                epinumber = name
            if "NW" in name:
                nwnumber = name

        if splnumber == None:
            splnumber = input("No spl-number found. Please specify:")

        if epinumber == None:
            epinumber = self.get_epi_from_spl(splnumber)

        if nwnumber == None:
            nwnumber = input("No spl-number found. Please specify:")

        return splnumber, epinumber, nwnumber


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

    def gaussian(x, a, x0, sigma, offset):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + offset


class Fitter():

    def __init__(self, f, xdata, ydata, p0=None, errors=None, startidx=None, stopidx=None, suppress_spanselector=False):
        """
        Parameters:
        xdata (np-array of floats): xdata to fit
        ydata (np-array of floats): ydata to fit
        p0 (tuple of floats): initial guess for parameters
        errors (np-array of floats): y-errors of fit data
        startidx (int): first index of fit range
        stopidx (int): last index of fit range
        suppress_spanselector (bool): if False, overwrite startidx and stopidx by selecting fit range in plot

        Returns:
        (tuple): (a (float), x0 (float), sigma (float), offset (float))
        """
        self.X, self.Y = xdata, ydata
        if startidx != None:
            self.X_fit, self.Y_fit = self.X[startidx:], self.Y[startidx:]
        if stopidx != None:
            self.X_fit, self.Y_fit = self.X_fit[:stopidx], self.Y_fit[:stopidx]

        self.startidx, self.stopidx = startidx, stopidx

        # self.initial_guess = self.create_initial_guess_single_peak(self.X_fit, self.Y_fit)

    def create_initial_guess_single_peak(self, xdata_fit, ydata_fit):
        """
        Create an initial guess for a single peak fit.

        Parameters:
        xdata_fit (np-array of floats): xdata to fit
        ydata_fit (np-array of floats): ydata to fit

        Returns:
        (tuple): (a (float), x0 (float), sigma (float), offset (float))
        """
        # Approximate amplitude based on maximum value within fit range
        a_idx = np.argmax(ydata_fit)
        a = ydata_fit[a_idx]

        # Approximate peak position based on x-value of maximum value within fit range
        x0 = xdata_fit[a_idx]

        # Approximate FWHM based on position of value which first exceeds half of maximum value when iteration over values
        for x, y in zip(xdata_fit, ydata_fit):
            if y >= a/2:
                sigma = (x0-x) / np.sqrt(2*np.log(2)) # FWHM = 2 * (x0-x); sigma = FWHM/(2*sqrt(2*ln2))
                break

        # Approximate offset based on average of first and last value of fit range
        offset = 0.5 * (ydata_fit[0] + ydata_fit[-1])

        return a, x0, sigma, offset


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

fit = SpanSelector()
fit.select_x_span(x, y)

