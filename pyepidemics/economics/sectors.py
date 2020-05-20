import pandas as pd
import numpy as np

SECTORS= ["agriculture", "energie", "industrie-alimentaire", "industrie-coke", "industrie-biens", "industrie-transport", "industrie-autres",
 "construction", "commerce", "transport", "hebergement-restauration", "information-communication", "finance", "immobilier", 
 "services", "service-public", "autres"]

#part du secteur dans le pib
base = [0.02,
    0.02,
    0.02,
    0.00,
    0.01,
    0.01,
    0.06,
    0.06,
    0.10,
    0.05,
    0.03,
    0.05,
    0.04,
    0.13,
    0.14,
    0.22,
    0.03, 
]
#productivity
TAU_confinement= [0.88,
    0.79, 
    0.90,
    0.33,
    0.42,
    0.33,
    0.49,
    0.14,
    0.50,
    0.44,
    0.18,
    0.71,
    0.90,
    0.96,
    0.57,
    0.89,
    0.41
]
TAU_activite_partiel =[
    0.98,
    0.79,
    1.04,
    0.34,
    0.57,
    0.33,
    0.58,
    0.57,
    0.61,
    0.51,
    0.42,
    0.76,
    0.92,
    1.04,
    0.69,
    0.93,
    0.56
]
TAU_ecole =[
    0.96,
    0.80,
    0.95,
    0.35,
    1.23,
    1.00,
    0.84,
    1.00,
    0.84,
    0.80,
    1.0,
    0.97,
    1.0,
    0.96,
    0.91,
    0.94,
    0.68
]
TAU_fermeture=[
    1.0,
    0.8,
    1,
    0.4,
    1,
    0.3,
    0.9,
    0.1,
    0.7,
    0.8,
    0.4,
    1.0,
    1,
    1.0,
    1.0,
    0.9,
    0.6
]
TAU_tt= [
    1.0,
    0.8,
    1.1,
    0.4,
    1.3,
    0.3,
    0.9,
    0.1,
    0.9,
    0.8,
    0.2,
    1.0,
    1.1,
    1.0,
    1.0,
    1.0,
    0.7
]
TAU_reconfinement =[0.9,
    0.4,
    1.2,
    0.3,
    1,
    0.2,
    0.4,
    0.1,
    0.4,
    0.3,
    0.3,
    0.7,
    1,
    1,
    0.5,
    0.8,
    0.2
]
TAU_chomageST=[
    0.98,
    0.80,
    1.00,
    0.36,
    1.00,
    0.80,
    0.84,
    0.57,
    1.01,
    0.79,
    0.42,
    0.95,
    1.02,
    1.01,
    0.89,
    1.02,
    0.78
]

TAU_activite_partielle_DARES=[
    0.99,
    0.99,
    1.00,
    0.98,
    1.00,
    0.97,
    0.99,
    0.85,
    0.89,
    0.89,
    0.79,
    0.92,
    0.98,
    0.93,
    0.82,
    0.98,
    0.91
]

TAU_LT=[
    1.0,
    0.8,
    1.0,
    0.4,
    1.0,
    0.8,
    0.8,
    0.8,
    1.0,
    0.8,
    0.8,
    1.0,
    1.0,
    1.0,
    0.9,
    1.0,
    0.8,
]

tau =[base, TAU_confinement,TAU_activite_partiel, TAU_ecole, TAU_fermeture,TAU_tt,TAU_chomageST,TAU_reconfinement, 
    TAU_activite_partielle_DARES,TAU_LT]

strategies = ['eq', 'confinement', 'activite-partielle-(ofce)', 'fermeture-ecole', 'fermeture-obligatoire', 'tt', 
    'chomageST', 'reconfinement',  'activite-partielle-(dares)', 'Recovery' ]

def sectors_productivity(strategies):
    productivity ={}
    for t, strategy in zip(tau,strategies):
        productivity[strategy] = dict(zip(SECTORS, t))
    return productivity

