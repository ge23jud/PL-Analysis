from scipy.optimize import curve_fit

class Fitter():

    def __init__(self, f, xdata, ydata, p0=None, error=None, fitrange=[None, None]):
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

        Returns:
        ?
        """
        self.f = f
        self.X, self.Y, self.error = xdata, ydata, error
        if callable(fitrange):
            self.fitrange = fitrange(self.X, self.Y)
        else:
            self.fitrange = fitrange
        self.X_fit, self.Y_fit = self.X[self.fitrange[0]:self.fitrange[1]], self.Y[self.fitrange[0]:self.fitrange[1]]
        if self.error is not None:
            self.error_fit = self.error[fitrange[0]:fitrange[1]]
        else:
            self.error_fit = self.error

        if callable(p0):
            self.p0 = p0(self.X_fit, self.Y_fit)
        else:
            self.p0 = p0

        self.opt, self.cov = self.fit()

    # def set_fitrange(self, fitrange):
    #     """
    #     Change self.X_fit, self.Y_fita and self.error_fit.
    #
    #     Parameters:
    #     Returns:
    #     tuple: (a, x0 , sigma , offset) -> Initial guesses for amplitude, peak position, peak width and offset
    #     """

    def fit(self):
        """
        Perform scipy.curve_fit on self.X_fit and self.Y_fit.

        Returns:
        tuple (p), array (p, p): optimized fit parameters, covariance matrix
        """
        opt, cov = curve_fit(self.f, self.X_fit, self.Y_fit, self.p0, self.error_fit)
        return opt, cov

