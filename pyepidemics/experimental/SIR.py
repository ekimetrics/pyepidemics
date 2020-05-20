import matplotlib.pyplot as plt
import numpy as np
from sympy import dsolve
import scipy.integrate as spi

from utils import plot_res

beta = 1.4247
gamma = 0.14286

TS = 1.0
ND = 70.0

I0 = 1e-6
S0 = 1-I0

inputs = (S0, I0, 0.0)

def sir(inputs, time):  
    """The main set of equations"""
    Y=np.zeros((3))
    V = inputs    
    Y[0] = - beta * V[0] * V[1]
    Y[1] = beta * V[0] * V[1] - gamma * V[1]
    Y[2] = gamma * V[1]
    return Y

if __name__=="__main__":
    
    t_start = 0.0; t_end = ND; t_inc = TS
    t_range = np.arange(t_start, t_end+t_inc, t_inc)
    
    res = spi.odeint(sir, inputs, t_range)

    plot_res(res)