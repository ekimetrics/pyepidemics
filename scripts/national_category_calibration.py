# Base Data Science snippet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import math
import scipy.special as sp

import sys
sys.path.append("../")

from pyepidemics.models.examples.covid_category import COVID19Category
from pyepidemics.dataset import get_contact_matrices, fetch_daily_case_france
from pyepidemics.utils import clean_series

from scipy.optimize import curve_fit

cases = fetch_daily_case_france()

n_extend = 50
data_extended = {}

def logistic_f(X, c, k, m):
    y = c / (1 + np.exp(-k*(X-m)))
    return y

def gaussian_f(X, a, mu, sigma):
    y = a * np.exp(-0.5 * ((X-mu)/sigma)**2)
    return y

def skew2(x,  a,mu,sigma,alpha,c):
    normpdf = (1 / (sigma * np.sqrt(2 * math.pi))) * np.exp(-(np.power((x - mu), 2) / (2 * np.power(sigma, 2))))
    normcdf = (0.5 * (1 + sp.erf((alpha * ((x - mu) / sigma)) / (np.sqrt(2)))))
    return 2 * a * normpdf * normcdf + c, max(normpdf)

def skew(x, sigmag, mu, alpha, c, a):
    return skew2(x, sigmag, mu, alpha, c, a)[0]

for col in ["ICU","H"]:
    data_col = cases[col].values
    model,cov = curve_fit(skew,xdata = np.arange(len(data_col)),ydata = data_col,p0=[np.max(data_col), np.argmax(data_col),1,1,1])
    x = np.arange(len(cases)+n_extend)
    data_extended[col] = skew(x,*model)

for col in ["D"]:
    data_col = cases[col].values
    model,cov = curve_fit(logistic_f,xdata = np.arange(len(data_col)),ydata = data_col)
    x = np.arange(len(cases)+n_extend)
    data_extended[col] = logistic_f(x,*model)

index = pd.date_range(start = cases.index[0],periods = len(cases) + n_extend)
data_extended = pd.DataFrame(data_extended,index = index)

cases_extended = cases[["ICU","H","D"]].copy().append(data_extended.iloc[-n_extend:])


N = [13.45e6, 36.05e6, 15.39e6]
init_state = {"S_young":13.45e6, "S_adult": 36.05e6 - 1.0, "S_senior": 15.39e6, "E_young":0.0, "E_adult": 1.0, "E_old": 0.0}

space = {
    "beta_young":(0.1,1),
    "beta_adult":(0.1,1),
    "beta_senior":(0.1,1),
    "offset":(0,10),
    "proba_icu_adult":(0.33, 0.39),
    "proba_icu_senior":(0.18, 0.22),
    "recovery_duration_hospital_adult":(10,15),
    "recovery_duration_hospital_senior":(40,50),
    "recovery_duration_icu_adult":(18, 22),
    "recovery_duration_icu_senior":(22, 32),
    "death_duration_icu_adult":(120, 150),
    "death_duration_icu_senior":(30, 40),
    "death_duration_hospital_adult":(200,280),
    "death_duration_hospital_senior":(50,80),
}

def constraint(model, loss):
    r0 = model.r0()
    if r0 < 3.25 or r0 > 3.4:
        return loss*10

    else:
        return loss

lockdown_start_date = 53
school_closure_date = 43 

class Model(COVID19Category):
    def __init__(self,params = None):
        if params is not None:
            self.reset(params)

    def reset(self,params):
        coeffs = {
            "domicile": {"dates": [0],"values":[0.1]},
            "ecoles": {"dates": [0, school_closure_date], "values": [1, 0]},
            "travailClos": {"dates": [0, lockdown_start_date], "values": [1, 0]},
            "chezProchesLieuxClos": {"dates": [0, lockdown_start_date], "values": [1, 0]},
            "autresLieuxClos(resto..)": {"dates": [0, lockdown_start_date], "values": [1, 0]},
            "transport": {"dates": [0, lockdown_start_date], "values": [1, 0]},
            "ouvert": {"dates": [0, lockdown_start_date], "values": [1, 0]}
        }
        super().__init__(
            N = N,
            beta = [params["beta_young"], params["beta_adult"], params["beta_senior"]],
            offset = params["offset"],
            proba_icu = [0, params["proba_icu_adult"], params["proba_icu_senior"]],
            recovery_duration_icu = [0, params["recovery_duration_icu_adult"], params["recovery_duration_icu_senior"]],
            recovery_duration_hospital = [0, params["recovery_duration_hospital_adult"], params["recovery_duration_hospital_senior"]],
            death_duration_hospital = [0, params["death_duration_hospital_adult"], params["death_duration_hospital_senior"]],
            death_duration_icu = [0, params["death_duration_icu_adult"], params["death_duration_hospital_senior"]],
            contact_coeffs = coeffs
        )

        self.calibrated_params = params

model = Model()
model.fit(cases_extended[["D","H","ICU"]], space, init_state, constraint = constraint, n = 1000, early_stopping = 300)






