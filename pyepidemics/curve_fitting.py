"""Inspiration
https://medium.com/analytics-vidhya/how-to-predict-when-the-covid-19-pandemic-will-stop-in-your-country-with-python-d6fbb2425a9f
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import scipy.special as sp
from scipy.optimize import curve_fit

def logistic_fn(X, a, mu,k):
    y = a / (1 + np.exp(-k*(X-mu)))
    return y

def gaussian_fn(X, a, mu, sigma):
    y = a * np.exp(-0.5 * ((X-mu)/sigma)**2)
    return y


def skew_helper(X,a,mu,sigma,alpha,c):
    normpdf = (1 / (sigma * np.sqrt(2 * math.pi))) * np.exp(-(np.power((X - mu), 2) / (2 * np.power(sigma, 2))))
    normcdf = (0.5 * (1 + sp.erf((alpha * ((X - mu) / sigma)) / (np.sqrt(2)))))
    return 2 * a * normpdf * normcdf + c, max(normpdf)


def skewed_gaussian_fn(X,a,mu,sigma,alpha,c):
    return skew_helper(X,a,mu,sigma,alpha,c)[0]




class CurveFittingModel:
    def __init__(self,fn):

        self._options_fn_str = ["logistic","gaussian","skewed_gaussian"]

        # Parse string parameter
        if isinstance(fn,str):
            self.fn_str = fn
            if fn == "logistic":
                fn = logistic_fn
            elif fn == "gaussian":
                fn = gaussian_fn
            elif fn == "skewed_gaussian":
                fn = skewed_gaussian_fn
            else:
                raise Exception(f"Unrecognized function str abbreviation {fn}, should be in {self._options_fn_str}")
        else:
            self.fn_str = None

        # Store function as attribute
        self.fn = fn


    def fit(self,data,p0 = None):

        if isinstance(data,pd.Series): data = data.values

        p0 = self._make_p0(data,p0)

        self.data = data
        self.length_fit = len(data)
        self.params,self.cov = curve_fit(self.fn,
                     xdata = np.arange(self.length_fit),
                     ydata = data,
                     p0 = p0
                     )

        return self.params


    def _make_p0(self,data,p0 = None):

        if p0 is not None:
            return p0
        else:
            if self.fn_str is not None:
                if self.fn_str == "gaussian":
                    return [np.max(data), np.argmax(data), 1]
                elif self.fn_str == "skewed_gaussian":
                    return [np.max(data), np.argmax(data),1,1,1]

            return None




    def predict(self,n = 0,show_fit = False):
        
        x = np.arange(self.length_fit+n)
        pred = self.fn(x,*self.params)

        if show_fit:

            plt.figure(figsize = (15,4))
            plt.plot(self.data)
            plt.plot(pred)
            plt.show()


        return pred


    def fit_predict(self,data,n = 0,show_fit = False,p0 = None):
        self.fit(data,p0 = p0)
        return self.predict(n,show_fit = show_fit)