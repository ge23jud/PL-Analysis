from plistlib import loads

from data_handler import DataHandler
from helper_functions import HelperFunctions


class Measurement:
    # Parent class for any type of single measurement curve
    # All specific measurement classes e.g. spectrum inherit from this class

    def __init__(self, data, filepath):

        # Info extracted from filepath
        self.filepath = filepath
        self.spl, self.epi, self.nw = HelperFunctions().get_info_from_filepath(filepath)

        self.info, self.X, self.Y = self.load(data, self.filepath)


    def display(self):
        print("location: ", self.filepath)
        print("spl-number: ", self.spl)
        print("Epi-number: ", self.epi)
        print("NW: ", self.nw)
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


class Spectrum(Measurement):

    def __init__(self, data, filepath):
        super().__init__(data, filepath)
        self.energy = self.X
        self.intensity = self.Y
        self.wavelength = HelperFunctions().nm_to_ev(self.energy)
        print("Center wavelength not implemented yet")
        attributes = ["date", "type", "temperature", "int_time", "power", "disp_window", "entrance_slit_width", "exit_slit_width"] # Info for Spectrum-type measurement
        for key, attr in zip(self.info.keys(), attributes):
            setattr(self, attr, key) # Split self.info into separate attributes