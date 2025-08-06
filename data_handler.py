import numpy as np


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

