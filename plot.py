import numpy as np
import matplotlib.pyplot as plt

class Plot():


    def add_curve(self, ax, xdata, ydata):
        ax.plot(xdata, ydata)


    def quickplot(self, xdata, ydata):
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        ax.plot()