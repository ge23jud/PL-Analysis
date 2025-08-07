import numpy as np
import matplotlib.pyplot as plt

class Plot():

    def add_curve(self, ax, xdata, ydata):
        ax.plot(xdata, ydata)
