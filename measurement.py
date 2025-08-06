from data_handler import DataHandler
from helper_functions import HelperFunctions


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
