from idlelib.format import reformat_comment

import numpy as np
import matplotlib.pyplot as ptl
from scipy.optimize import curve_fit
import re
import pandas as pd

SampleOverview_dir = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\Sample Overview.xlsx"

class HelperFunctions():

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

        self.filepath = filepath

        ## Info ##
        if self.filepath[-6:] == "origin":
            self.info, self.X, self.Y = DataHandler().load_origin()
        else:
            print("Filetype other than .origin found. Loading this type of data not yet implemented.")


class Spectrum(Measurement):

    def __init__(self, filepath):
        super().__init__(filepath)
        self.X += 1

    def show(self):
        print(self.X)


# path = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\20250715-plm0001_spl2411_spl2407_spl2415_spl2505\20250715_Epi-1780_NW6-12\Si-reference\Si-reference_000.origin"
# x = DataHandler().load_origin(path)[2]
# print(x)

# handler = DataHandler()
helper = HelperFunctions()
print(helper.get_epi_from_spl("spl2526"))



