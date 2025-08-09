from helper_functions import HelperFunctions

class MeasurementSeries():

    def __init__(self, data, filepath):
        """
        Series of m measurements with n_m data points, respectively. n_m can be different for every single measurement.
        Every measurement itself is of type Measurement(). The list of measurements read from file.

        Parameters:
        data (func): function to be used to load data. Returns
        filepath (str): Filepath of the file from which data is loaded
        """
        self.info, self.X, self.Y = self.load()


    def load(self, data, filepath):
        """
        Series of m measurements with n_m data points, respectively. n_m can be different for every single measurement.
        Every measurement itself is of type Measurement(). The list of measurements read from file.

        Parameters:
        data (func): function to be used to load data. Takes filepath as an argument and returns tuple (dic, array (n,n), array (n,n))
        filepath (str): Filepath of the file from which data is loaded
        """
        return data(filepath)