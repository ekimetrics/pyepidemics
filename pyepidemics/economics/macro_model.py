# Base Data Science snippet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import math
from tqdm import tqdm_notebook
import datetime

from .data import EconomicsData, HealthModel
from .sectors import sectors_productivity, SECTORS, strategies

class MacroModel(object):
    """macroeconomics model to model economics response given a deconfinement strategy"""
    def __init__(self, model, deconfinement_start='2020-05-11', horizon_days = 30):
        
        self.confinement = '2020-03-17'
        self.deconfinement= deconfinement_start

        """economics data as hypothesis"""
        ED = EconomicsData() #replace to workin excel
        self.df = ED.df.fillna(0)
        self.df_dept = ED.df_dept.set_index("dept_num").fillna(0)

        self.productivity= sectors_productivity(strategies)
        
        """input model from models"""
        HM = HealthModel("test")
        self.X = HM.X #strategie deconfinement
        self.x_actif = self.X['actif']
        self.x =self.X['total']

        self.horizon = horizon_days #HM.horizon (nb jours)TO DO
        self.start_index= self.df[self.df['ds'] ==self.confinement].index[0]
        self.end_index= self.df[self.df['ds'] ==self.deconfinement].index[0]
        self.horizon_index= self.horizon + self.end_index
        
################################################################
    #### EFFECTIVE PRODUCTION ####
    def effective_production(self, sector, strategy, **kwargs):
        """production according to y=k*l"""
        Y_tilde={}
        Y_tilde[sector] = 100
        for s in strategy: 
            Y_tilde[sector] = Y_tilde[sector]*self.productivity[s][sector]
        return Y_tilde

    def production_sector(self, sectors=SECTORS, strategy=[], **kwargs):
        """projection for pib by sector"""
        for sector in sectors:
            for i in range(self.start_index, self.end_index):
                self.df[sector][i] = self.effective_production(sector= sector, strategy = ['confinement'])[sector]
            for i in range(self.end_index, self.horizon_index):
                j=i-self.start_index
                self.df[sector][i] = self.effective_production(sector= sector, strategy = strategy )[sector]*self.x_actif[j]+(1-self.x_actif[j])*self.effective_production(sector= sector,strategy = ['confinement'])[sector]
            #hypothese 3 mois de chomageST
            for i in range(self.horizon_index, self.horizon_index+ 90):
                self.df[sector][i] = self.effective_production(sector= sector, strategy = ['chomageST'])[sector]
            for i in range(self.horizon_index+91, len(self.df)):
                self.df[sector][i] = self.effective_production(sector= sector, strategy = ['Recovery'])[sector]
        return 


    def production_dept(self, dept_num, strategy= ['chomageST'], sectors= SECTORS,**kwargs):
        """projection for pib for 1 dept"""
        self.production_sector(sectors= sectors, strategy = strategy)
        y_dept = "y_"+ str(dept_num)
        self.df[y_dept]=sum(self.df[sector]*self.df_dept[sector][dept_num]/100 for sector in sectors)
        return 
    

    def production_nat(self, method ="sector", strat = [], dept_confine = None):
        """projection for pib production for France incl.domtom"""
        self.production_sector(strategy = strat)
        self.df['y_projection']=sum(self.df[sector]*self.productivity['eq'][sector] for sector in SECTORS)
        if method == "sector":
            pass
        elif method == "dept":     
            self.DEPT  = self.df_dept.index.to_list()
            to_remove = ['FR', 'F', 'M']
            for x in to_remove:
                self.DEPT.remove(x)
            for d in self.DEPT:
                if d in dept_confine:
                    self.production_dept(d, strategy = ['confinement'])
                    y_dept = "y_"+ str(d)
                    x  = self.df['y_projection'] - self.df[y_dept]
                    self.df['y_projection']= self.df['y_projection']- x*self.df_dept["contrib_pib_emplois_pondere"][d]
                else: 
                    pass
                    #self.production_dept(d)
        return


    def production_sector_date(self,start_date, horizon, sectors=SECTORS, strategy=[],**kwargs):
        """projection for pib by sector"""  
        start_index=self.df[self.df['ds'] == start_date].index[0] 
        horizon_index=start_index+ horizon
        for sector in sectors:
            for i in range(start_index, horizon_index):
                self.df[sector][i] = self.effective_production(sector= sector, strategy = ['confinement'])[sector]
        return
    
    def reconfinement_nat(self, start_date, horizon, sectors=SECTORS,**kwargs):
        self.production_sector_date(start_date, horizon, sectors=SECTORS, strategy=['reconfinement'])
        self.df['y_projection']=sum(self.df[sector]*self.productivity['eq'][sector] for sector in SECTORS)
        return

#################################################################
    #### SAVINGS #####
    def savings(self):
        """saving from confinement period from production differential"""
        Y_eq= self.df['pib'][self.start_index -1]
        Y_tilde= self.effective_production()
        dS= [Y_eq-Y_tilde[i] for i in range(self.horizon)]
        return dS

    #### CONSUMPTION ####
    def consumed_from_saving(self, rate):
        """play here"""
        alpha =[0 for i in range(self.horizon)]
        start_deconfinement = self.horizon_index - self.end_index
        for i in range( self.horizon):
            j= i-self.start_index
            if i<start_deconfinement+(self.horizon-start_deconfinement)/2:
                alpha[i]= rate*j/15
            else:
                alpha[i]= (rate*((self.horizon-start_deconfinement)/2-j) +rate*self.horizon/2 ) /15
        return alpha

###############################################################
    #### FORECAST ####  
    def projection(self):
        """projection for production and consumption"""
        #consumption from deconfine people + from confine
        C_eq=self.df['C'][0]
        Y_eq= self.df['pib'][0]
        
        alpha= self.consumed_from_saving(0.3)#additional consumtion from extra savings
        dS = self.savings()

        C_dec = [(C_eq+alpha[i]*dS[i])*self.x[i] + (C_eq-dS[i])*(1-self.x[i]) for i in range(self.horizon)]
        #production
        pib_dec = [Y_eq + ((alpha[i]+1)*self.x[i]-1)*dS[i] for i in range(self.horizon)]

        return C_dec, pib_dec

    def reconciliate(self):
        """ reconciliation with input data for vizualisation """
        C_dec, pib_dec = self.projection()

        #consumption&production values in confinement
        for i in range(self.start_index, self.horizon_index):
            j= i-self.start_index
            self.df['pib'][i]= pib_dec[j]
            self.df['C'][i]= C_dec[j]
        return

