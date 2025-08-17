import numpy as np
from pandas import read_csv

from helper_functions import HelperFunctions


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
        data_start_idx = 14

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

        n = df.shape[0] - 1
        m = df.shape[1] - 1
        xdata = np.zeros((n+1, m))
        ydata = np.zeros((n, m))

        df = np.array(df)
        xdata[0, :] = df[0, 1:]
        for i in range(m):
            xdata[1:, i] = df[1:, 0].astype("float")

        ydata = df[1:, 1:]

        return header_dict, xdata, ydata

