

from ..dataset import get_contact_matrices
import numpy as np


def sigmoid_response(t,start_date,start,end,duration,interval = 0.95):
    """Sigmoid response
    Normally formula is end + (start - end) / ( 1 + exp(-k(-t + inflection)))
    Here for more control, we replace k by two parameters to control duration for a shift of an intensity of an interval
    By reversing the formula we get k = 2/duration * log (interval/(1-interval))
    Inflection becomes simply start_date + duration/2
    """
    k = 2/duration * np.log(interval/(1 - interval))
    inflection = start_date + duration/2
    return (start-end) / (1 + np.exp(-k*(-t+inflection))) + end


def multiple_sigmoid_response(t,start,values,dates,durations,interval = 0.95):

    duration = durations[0] if isinstance(durations,list) else durations

    yt = sigmoid_response(t,dates[0],start,values[0],duration,interval)

    for i in range(len(values[1:])):
        i = i+1
        duration = durations[i] if isinstance(durations,list) else durations
        yt += sigmoid_response(t,dates[i],0,values[i] - values[i-1],duration,interval)

    return yt


matrices = get_contact_matrices()["non"]
def contact_matrix_response(y, t, start, end, coeffs, coeffs_deconfinement=None, seniors=False):
    if t >= start and t < end:
        return {"category" : np.sum([coeffs[k]*matrices[k] for k in matrices.keys()],
                                   axis=0)}

    elif t < start or (t >= end and coeffs_deconfinement is None):
        #matrices["domicile"] *= 0.1
        to_return = {"category" : np.sum([matrices[k] for k in matrices.keys()], axis=0)}
        return flag, to_return

    else:
        seniors_mat = {k:np.identity(3) for k in matrices.keys()}
        if seniors:
            for k in ["ecoles", "travailClos", "chezProchesLieuxClos", "autresLieuxClos(resto..)", "transport", "ouvert"]:
                seniors_mat[k][2,2] = 0

        return flag, {"category" : np.sum([coeffs_deconfinement[k]*seniors_mat[k] @ matrices[k] for k in matrices.keys()],
                                   axis=0)}

def case_isolation_response(y, t, start, value, end=np.infty):
    if t < start:
        return 0
=======
    else:
        return {"category" : np.sum([matrices[k] for k in matrices.keys()],
                                    axis=0)}
>>>>>>> 93f8e1f52d0ccfa20733c0a163e2b8c9c2efea46:pyepidemics/policies/utils.py

