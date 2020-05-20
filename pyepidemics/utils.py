"""Helper functions
"""
import json

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
import statsmodels.api as sm

def smooth_series(y,p = 6.25):
    """Smooth a series in a dataframe using Hodrick Prescott Filter
    """
    cycle, trend = sm.tsa.filters.hpfilter(y, p)
    return trend


def clean_series(y,smooth = False,p = 6.25,logsmooth = True):
    """Clean outliers in a series in a dataframe
    """

    # Remove null values in the middle of the series using interpolate
    # First null values are not interpolated but later filled by 0.0
    y = y.replace(0.0,np.NaN).interpolate().fillna(0.0)

    # Smooth using Hodrick Prescott filter with parameter p
    if smooth:
        y = smooth_series(y,p)
        y.loc[(y < 1) & (y > 0)] = 1

    if logsmooth:
        y = y.map(lambda x : np.log(1+x))
        y = smooth_series(y,p)
        y = y.map(lambda x : np.exp(x) - 1)
        y.loc[(y < 1) & (y > 0)] = 1
        y.loc[y < 0] = 0

    return y

def load_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return data

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)