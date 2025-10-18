import numpy as np
from scipy import constants
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from data_handler import DataHandler
import re

SampleOverview_dir = r"\\nas.ads.mwn.de\tuze\wsi\e24\SQN\Researchers\Haubmann Benjamin\01_PhD\Sample Overview.xlsx"

class HelperFunctions():

    def nm_to_ev(self, input):
        """
        Convert energy to wavelength and vice versa.

        Args:
            input (array/float): wavelength [m] or energy [eV]

        Returns:
            array/float: wavelength [m] or energy [eV]
        """
        return  constants.h * constants.c / constants.e / input

    def reformat_splnumber(self, splnumber):
        """
        Transform spl-number from format splXXXX to format XX-XX.

        Args:
            splnumber (str): spl-number in format splXXXX

        Returns:
            str: spl-number in format XX-XX
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
            str: spl-number
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
            nwnumber = input("No NW-number found. Please specify:")

        return splnumber, epinumber, nwnumber

    def get_inttime_centerenergy_from_filepath(self, filepath):

        int_time, center_energy = None, None
        filename = filepath.split("\\")[-1]
        parts = filename.split("_")
        for p in parts:
            if "ev" in p.lower():
                center_energy = p
            if bool(re.match(r'^\d+\.?\d*s$', p)):
                int_time = p

        if int_time == None:
            print("Integration time not found in filename")
        if center_energy == None:
            print("Center energy not found in filename")

        return int_time, center_energy

    def select_files(self):
        """
        Opens a file dialog to select one or multiple files.
        Returns a list of full paths of the selected files, or empty list if canceled.
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window

        file_paths = filedialog.askopenfilenames(
            title="Select file(s) - Hold Ctrl/Cmd to select multiple",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("CSV files", "*.csv"),
                ("Origin files", "*.origin")
            ]
        )

        root.destroy()
        return list(file_paths) if file_paths else []


    def load_selector(self, filepath):

        filepath_full = filepath
        filepath = filepath.split("\\")
        format = filepath[-1].split(".")[-1]


        if format == "origin":

            with open(filepath_full, 'r', encoding='iso-8859-1') as file:
                lines = file.readlines()
                meastype = lines[1].strip().split("\t")[1]

            if meastype == "X vs Y/Power HWP position vs. Power":
                return DataHandler().load_origin_powercalibration

            elif meastype == "X vs Y/Power HWP position vs. Photoluminescence":
                return DataHandler().load_series_origin

            elif meastype == "Photoluminescence":
                return DataHandler().load_origin


    def convert_info_spectrum(self, key, value):

        if key == "Date" or key == "Measurement type":
            return value

        elif key in ["Temperature", "Integration time", "Excitation power", "Entrance slit width", "Exit slit width"]:
            return float(value.split(" ")[0])

        elif key in ["Center wavelength", "Dispersion window"]:
            return float(value.split("/")[1].strip().split(" ")[0])


    def find_closest_index(self, array, value):

        closest_index = np.argmin(np.abs(array - value))

        return closest_index


    def FWHM_from_sigma(self, sigma):
        return 2*np.sqrt(2*np.log(2)) * sigma