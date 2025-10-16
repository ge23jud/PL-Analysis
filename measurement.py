import os.path
from hmac import digest_size
from plistlib import loads
import matplotlib.pyplot as plt

from data_handler import DataHandler
from helper_functions import HelperFunctions


class Measurement():
    # Parent class for any type of single measurement curve
    # All specific measurement classes e.g. spectrum inherit from this class

    def __init__(self, data, filepath):

        # Info extracted from filepath
        self.filepath = filepath
        self.filename = filepath.split("\\")[-1]
        if "spl" in self.filename.lower():
            self.spl, self.epi, self.nw = HelperFunctions().get_info_from_filepath(filepath)

        self.info, self.X, self.Y = self.load(data, self.filepath)


    def display(self):
        print("location: ", self.filepath)
        #print("spl-number: ", self.spl)
        #print("Epi-number: ", self.epi)
        #print("NW: ", self.nw)
        for key in self.info.keys():
            print(key, self.info[key])


    def load(self, data, filepath=None):
        """
        Load info and data of measurement.

        Parameters:
        data (tuple (dic, array, array) or func): (info, xdata, ydata) or function which takes "filepath" as argument and returns the same
        filepath (str): If data is function, it is passed to data

        Returns:
        tuple (dic, array, array): info, xdata, ydata
        """
        if callable(data):
            return data(filepath)
        else:
            return data


    def plot(self):
        fig, ax = plt.subplots(1, 1, figsize=(4, 5))
        ax.plot(self.X, self.Y)
        plt.show()


class Spectrum(Measurement):

    def __init__(self, data, filepath):
        super().__init__(data, filepath)
        self.energy = self.X
        self.intensity_raw = self.Y
        self.wavelength = HelperFunctions().nm_to_ev(self.energy)

        attributes = ["date", "type", "temperature", "int_time", "power_bs", "center_energy", "disp_window", "entrance_slit_width",
                      "exit_slit_width"]  # Info for Spectrum-type measurement
        for key, attr in zip(self.info.keys(), attributes):
            setattr(self, attr, HelperFunctions().convert_info_spectrum(key, self.info[key]))  # Split self.info into separate attributes


        # find and load dark spectrum
        self.int_time_str, self.center_energy_str = HelperFunctions().get_inttime_centerenergy_from_filepath(self.filepath)
        self.dark_filepath = DataHandler().find_dark(os.path.dirname(self.filepath), self.int_time_str, self.center_energy_str)
        self.dark_loadfunction = HelperFunctions().load_selector(self.dark_filepath)
        self.dark = DarkSpectrum(self.dark_loadfunction, self.dark_filepath)

        # subtract dark spectrum
        self.intensity = self.Y - self.dark.Y

        # find and load power calibration
        self.calibration_filepath_bs, self.calibration_filepath_sample = DataHandler().find_powercalibration(os.path.dirname(self.filepath))
        self.calibration_loadfunction = HelperFunctions().load_selector(self.calibration_filepath_bs)
        self.calibration_bs = PowerCalibration(self.calibration_loadfunction, self.calibration_filepath_bs)
        self.calibration_sample = PowerCalibration(self.calibration_loadfunction, self.calibration_filepath_sample)
        self.calibration_pars = DataHandler().linear_powercalibration(self.calibration_filepath_bs, self.calibration_filepath_sample)

        # calculate power at sample
        self.power_sample = self.power_bs * self.calibration_pars[0]


    def plot(self):
        fig, ax = plt.subplots(1, 1, figsize=(4, 5))
        ax.plot(self.X, self.intensity)
        plt.show()


    def plot_raw(self):
        fig, ax = plt.subplots(1, 1, figsize=(4, 5))
        ax.plot(self.X, self.intensity_raw)
        plt.show()


class DarkSpectrum(Measurement):

    def __init__(self, data, filepath):
        super().__init__(data, filepath)
        self.energy = self.X
        self.intensity = self.Y
        self.wavelength = HelperFunctions().nm_to_ev(self.energy)


class PowerCalibration(Measurement):

    def __init__(self, data, filepath):
        super().__init__(data, filepath)
        self.hwp = self.X
        self.power = self.Y


class MeasurementSeries():
    def __init__(self, data, filepath):
        """
        Series of m measurements with n_m data points, respectively. n_m can be different for every single measurement.
        Every measurement itself is of type Measurement(). The list of measurements read from file.

        Parameters:
        data (func): function to be used to load data. Returns
        filepath (str): Filepath of the file from which data is loaded
        """
        # load is a separate method to allow to implement logic (different file types etc.) later without complicating constructor
        self.filepath = filepath
        self.filename = filepath.split("\\")[-1]
        self.info, self.X, self.Y = self.load(data, filepath)
        if "spl" in self.filename.lower():
            self.spl, self.epi, self.nw = HelperFunctions().get_info_from_filepath(filepath)


    def load(self, data, filepath):
        """
        Series of m measurements with n_m data points, respectively. n_m can be different for every single measurement.
        Every measurement itself is of type Measurement(). The list of measurements read from file.

        Parameters:
        data (func): function to be used to load data. Takes filepath as an argument and returns tuple (dic, array (n,n), array (n,n))
        filepath (str): Filepath of the file from which data is loaded
        """
        return data(filepath)


    def plot(self):
        fig, ax = plt.subplots(1, 1, figsize=(4, 5))
        for i in range(self.Y.shape[1]):
            ax.plot(self.X[1:, i], self.Y[:, i])
        plt.show()


class PowerSeries(MeasurementSeries):

    def __init__(self, data, filepath):
        super().__init__(data, filepath)
        self.power_bs = self.X[0, :]
        self.energy = self.X[1:, :]
        self.intensity_raw = self.Y
        self.wavelength = HelperFunctions().nm_to_ev(self.energy)

        attributes = ["date", "type", "temperature", "int_time", "power_bs", "center_energy", "disp_window",
                      "entrance_slit_width", "exit_slit_width"]  # Info for Spectrum-type measurement
        for key, attr in zip(self.info.keys(), attributes):
            if attr == "power_bs":
                continue
            setattr(self, attr, HelperFunctions().convert_info_spectrum(key, self.info[key]))  # Split self.info into separate attributes

        # find and load dark spectrum
        self.int_time_str, self.center_energy_str = HelperFunctions().get_inttime_centerenergy_from_filepath(self.filepath)
        self.dark_filepath = DataHandler().find_dark(os.path.dirname(self.filepath), self.int_time_str, self.center_energy_str)
        self.dark_loadfunction = HelperFunctions().load_selector(self.dark_filepath)
        self.dark = DarkSpectrum(self.dark_loadfunction, self.dark_filepath)

        # subtract dark spectrum
        self.intensity = self.intensity_raw[:, :]
        for i in range(self.intensity.shape[1]):
            self.intensity[:, i] = self.Y[:, i] - self.dark.Y


    def plot(self):
        fig, ax = plt.subplots(1, 1, figsize=(4, 5))
        for i in range(self.Y.shape[1]):
            ax.plot(self.energy[:, i], self.intensity[:, i])
        ax.set_xlabel("Energy (eV)")
        ax.set_ylabel("PL Intensity (arb. unit)")
        ax.set_yscale("log")
        plt.show()

