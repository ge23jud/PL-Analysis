import numpy as np

class FitFunctions():


    def single_gaussian_const_bg(self, x, a, x0, sigma, offset):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + offset


    def single_gaussian_linear_bg(self, x, a, x0, sigma, m, t):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + m * x + t


    def linear(self, x, a, b):
        return a*x + b


    def linear_wo_offset(self, x, a):
        return a*x


    def sigmoid(self, x, a, b, c, d):
        return a/(1+np.exp(-x*b+c)) + d


    def tanh(self, x, a, b, c, d):
        return a * np.tanh(b*x + c) + d