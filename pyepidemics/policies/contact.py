import numpy as np
from ..dataset import get_contact_matrices


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
    else:
        return {"category" : np.sum([matrices[k] for k in matrices.keys()],
                                    axis=0)}