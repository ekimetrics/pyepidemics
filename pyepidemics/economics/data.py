# Base Data Science snippet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import sys
import math

from ..dataset import fetch_production_economics
from .sectors import sectors_productivity, SECTORS, strategies

class EconomicsData(object):
    def __init__(self):
        self.df, self.df_dept = fetch_production_economics()


###### IMPORT COVID HEALTH MODEL##########
class HealthModel(object):
    def __init__(self, model):
        self.X, self.horizon = self.output_model(model)

    def output_model(self, model="test"):
        if model == "test":
            X, horizon = self.test_model()
        else:
            pass
        return X, horizon

    def test_model(self):
        """stratégie déconfinement sanitaire"""
        X={}
        start_deconfinement = 45 #45jours de confineemnt
        horizon = 150 #150j
        #actifs
        x =[0 for i in range(horizon)]
        x[0]= 0
        for i in range(start_deconfinement, horizon):
            j= i-start_deconfinement
            x[i] = 1/(1+math.exp(-j/10))
        X['actif'] = x
        #seniors
        x =[0 for i in range(horizon)]
        X['seniors'] = x
        #enfants
        x =[0 for i in range(horizon)]
        x[0]= 0
        for i in range(start_deconfinement , horizon):
            j= i-start_deconfinement
            x[j] = 1/(1+math.exp(-j/10))
        X['enfants'] = x
        #TOTAL
        x =[0 for i in range(horizon)]
        for i in range(start_deconfinement,horizon):
            x[i] = 0.6*X['actif'][i]+ 0.2*X['seniors'][i]+ 0.2*X['enfants'][i]
        X['total'] = x
        return X, horizon


