import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from plot import Plot

class Fitter():

    def __init__(self, f=None, xdata=None, ydata=None, error=None, p0=None, fitrange=[None, None]):
        """
        Tool for simple fits to experimental data

        Parameters:
        f (func): Fit function which takes p+1 arguments (1 independent variable, p parameters)
        xdata (array (n)): x-values of data
        ydata (array (n)): y-values of data
        * p0: initial guess for parameters / default: None
            - tuple (p): Direct specification of initial guesses
            - func: Function to autogenerate initial guesses
            - None: For running fit without initial guesses
        * errors (array (n)): y-errors of data
        * fitrange: Range of x-data to use for fit / default: [None, None]
            - list (2): Boundary indices of fit range; If None, no boundary is set
            - func: Function that returns boundary indices, e.g. by span selection

        """
        #self.set_all(f, xdata, ydata, p0, error, fitrange)


    def set_function(self, f):
        self.f = f


    def set_data(self, xdata, ydata, error):
        self.X, self.Y, self.error = xdata, ydata, error


    def set_p0(self, p0):
        self.p0 = p0


    def set_fitrange(self, fitrange):
        self.fitrange = fitrange
        print(self.Y)
        print(self.fitrange)
        self.X_fit, self.Y_fit = self.X[self.fitrange[0]:self.fitrange[1]], self.Y[self.fitrange[0]:self.fitrange[1]]
        if self.error is not None:
            self.error_fit = self.error[fitrange[0]:fitrange[1]]
        else:
            self.error_fit = self.error


    def set_all(self, f, xdata, ydata, error, p0, fitrange):
        self.set_function(f)
        self.set_data(xdata, ydata, error)
        # print(self.X)
        self.set_fitrange(fitrange)
        self.set_p0(p0)


    def fit(self, suppress_plot=False):
        """
        Perform scipy.curve_fit on self.X_fit and self.Y_fit.

        Returns:
        tuple (p), array (p, p): optimized fit parameters, covariance matrix
        """
        opt, cov = curve_fit(self.f, self.X_fit, self.Y_fit, self.p0, self.error_fit)
        self.opt, self.cov = opt, cov
        if not suppress_plot:
            self.plot()
        return opt, cov


    def plot(self):
        fig, ax = plt.subplots(1, 1)
        plotter = Plot()
        plotter.add_curve(ax, self.X, self.Y)
        plotter.add_curve(ax, self.X, self.f(self.X, *self.opt))
        plt.show()
