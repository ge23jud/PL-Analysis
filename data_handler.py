import numpy as np
from pandas import read_csv
import os

from fit_functions import FitFunctions
from fitter import Fitter

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


        with open(filepath, 'r', encoding='iso-8859-1') as file:
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
            elif line.startswith("Center wavelength"):
                parts = line.split("\t") # Center wavelength
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


    def load_origin_powercalibration(self, filepath):
        header_dict, Y, X = self.load_origin(filepath)
        return header_dict, X, Y


    def load_series_origin(self, filepath):
        """
        Load data series from a .origin file.

        Parameters:
        filepath (str): Path to the .origin file

        Returns:
        tuple: (info, X, Y) where:
            - info (dic): Dictionary with header information
            - X: (array (n+1,m)): Independent variables x1 and x2 (e.g. power and energy). [0, :]  are m values of x1, [:, i] are n values of x2 for i´th value of x1
            - Y: (array (n,m)) Dependent variable y (e.g. intensity)

        Note: Currently, this method is designed for a Powerseries, in particular, HWP Position is contained in
        "info". This is not the case in the case of a general measurement series.
        """
        with open(filepath, 'r') as file:
            lines = file.readlines()

        header_dict = {}
        header_stop_idx = 9  # first line after header
        data_start_idx = 13

        # Parse header information
        for i, line in enumerate(lines):

            if i == header_stop_idx:
                break

            line = line.strip()

            if not line or line.startswith("(") or line.startswith("Energy"):
                continue  # Skip empty lines or line which contain units
            else:
                parts = line.split(':', 1)  # Split line at first colon

            if len(parts) != 2:
                print(f"Error during loading of data. Number other than two columns found in line {i}")
                continue
            else:
                key = parts[0].strip()
                value = parts[1].strip()
                header_dict[key] = value

        df = read_csv(filepath, delimiter="\t", header=data_start_idx-2, encoding="unicode_escape")

        n = df.shape[0] - 2
        m = df.shape[1] - 1
        xdata = np.zeros((n+1, m))
        ydata = np.zeros((n, m))

        df = np.array(df)
        xdata[0, :] = df[0, 1:]
        for i in range(m):
            xdata[1:, i] = df[2:, 0].astype("float")

        ydata = df[2:, 1:]

        return header_dict, xdata, ydata


    def find_dark(self, filepath, int_time, center_energy):
        if filepath == r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\13_PL":
            print("No dark spectrum found.")
            return
        items = os.listdir(filepath)
        for x in items:
            if "dark" in x or "Dark" in x:
                fullpath = "\\".join((filepath, x))
                if os.path.isfile(fullpath):
                    if int_time in x and center_energy in x:
                        return fullpath
                elif os.path.isdir(fullpath):
                    return self.find_dark(fullpath, int_time, center_energy)
        return self.find_dark(os.path.dirname(filepath), int_time, center_energy)


    def find_powercalibration(self, filepath):
        if filepath == r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\13_PL":
            print("No power calibration found.")
            return
        items = os.listdir(filepath)
        for x in items:
            if "calibration" in x.lower():
                fullpath = "\\".join((filepath, x))
                if os.path.isfile(fullpath):
                    if "atbs" in x.lower():
                        path_bs = fullpath
                    elif "atsample" in x.lower():
                        path_sample = fullpath
                elif os.path.isdir(fullpath):
                    return self.find_powercalibration(fullpath)
        if path_bs == None or path_sample == None:
            return self.find_powercalibration(os.path.dirname(filepath))
        else:
            return path_bs, path_sample


    def linear_powercalibration(self, path_bs, path_sample):

        p_bs = self.load_origin_powercalibration(path_bs)[2]
        p_sample = self.load_origin_powercalibration(path_sample)[2]

        f = FitFunctions().linear_wo_offset
        fit_obj = Fitter(f, p_bs, p_sample, suppress_plot=True)

        return fit_obj.opt

