"""Custom COVID19 Compartmental model
"""
import numpy as np

from ..model import CompartmentalModel
from ..params import Params
from ...dataset import get_contact_matrices


class COVID19Category(CompartmentalModel):

    def __init__(self,
                 N,
                 beta,
                 incubation_duration = 3.7,
                 recovery_duration_asymptomatic = 4.7,
                 recovery_duration_mild = 4.7,
                 symptoms_to_hospital_duration = 5.5,
                 symptoms_to_icu_duration = 7,
                 recovery_duration_hospital = 17,
                 recovery_duration_icu = 8,
                 death_duration_hospital = 10,
                 death_duration_icu = 11,
                 proba_severe = [0, 0.1, 0.2],
                 proba_mild = 0.5,
                 proba_icu = 0.182,
                 categories=["young", "adult", "senior"],
                 contact_coeffs = None,
                 offset = None,
                 symptomatic_isolation=0.75,
                 case_isolation=0):

        # Prepare params
        dimensions = {"category":categories}
        self.coeffs = contact_coeffs
        params = Params(**dimensions)

        params.add({
            "N": N,
            "beta": beta,
            "incubation_duration": incubation_duration,
            "recovery_duration_asymptomatic": recovery_duration_asymptomatic,
            "recovery_duration_mild": recovery_duration_mild,
            "symptoms_to_hospital_duration": symptoms_to_hospital_duration,
            "symptoms_to_icu_duration": symptoms_to_icu_duration,
            "recovery_duration_hospital": recovery_duration_hospital,
            "recovery_duration_icu": recovery_duration_icu,
            "death_duration_hospital": death_duration_hospital,
            "death_duration_icu": death_duration_icu,
            "proba_severe": proba_severe,
            "proba_mild": proba_mild,
            "proba_icu": proba_icu,
            "offset": offset,
            "symptomatic_isolation": symptomatic_isolation,
        })

        # Define compartments name and number
        compartments = ["S","E","Ia","Im","Is","H","ICU","D","R"]
        super().__init__(compartments,dimensions = dimensions,params = params,offset = offset)

        # Parameters
        self.N = np.sum(N)
        case_isolation = self.make_callable(case_isolation) 

        # Prepare granular transition function
        def transitions(dimensions):

            # Prepare helper getter function
            g = lambda x,dimensions=dimensions : self.get(x,dimensions)

            # Get compartment names and parmas 
            S,E,Ia,Im,Is,H,ICU,R,D = g(["S","E","Ia","Im","Is","H","ICU","R","D"])

            # Precompute parameters
            p = {x:g(x) for x in self.params.columns}

            # Make callables
            beta = g("beta")
            beta = self.make_callable(beta)
            C = self.contact_matrix(dimensions)

            return {
                "S":{
                    "E":lambda y,t : beta(y,t) * y[S] * (1-case_isolation(y,t)) * (1/np.array(self.params["N"])) * C(y,t) @ (y["Ia"] + (1-p["symptomatic_isolation"])*y["Im"] + (1-p["symptomatic_isolation"])*y["Is"])
                },
                "E":{
                    "Ia":lambda y,t : 1/p["incubation_duration"] * (1 - p["proba_severe"] - p["proba_mild"]) * y[E],
                    "Im":lambda y,t : 1/p["incubation_duration"] * p["proba_mild"] * y[E],
                    "Is":lambda y,t : 1/p["incubation_duration"] * p["proba_severe"] * y[E],
                },
                "Ia":{
                    "R":lambda y,t : 1/p["recovery_duration_asymptomatic"] * y[Ia],
                },
                "Im":{
                    "R":lambda y,t : 1/p["recovery_duration_mild"] * y[Im],
                },
                "Is":{
                    "ICU":lambda y,t : 1/p["symptoms_to_icu_duration"] * p["proba_icu"] * y[Is],
                    "H":lambda y,t : 1/p["symptoms_to_hospital_duration"] * (1 - p["proba_icu"]) * y[Is],
                },
                "ICU":{
                    "R":lambda y,t : 1/p["recovery_duration_icu"]  * y[ICU],
                    "D":lambda y,t : 1/p["death_duration_icu"] * y[ICU],
                },
                "H":{
                    "R":lambda y,t : 1/p["recovery_duration_hospital"] * y[H],
                    "D":lambda y,t : 1/p["death_duration_hospital"] * y[H],
                }
            }

        # Add transitions
        self.transitions = transitions
        self.add_transitions(transitions,granularity=True)

    def contact_matrix(self, dimensions, get_vacations=False):
        vacations = "oui" if get_vacations else "non"
        matrices = get_contact_matrices()[vacations]
        if dimensions == "all":
            return lambda y, t: np.sum([self.make_callable(self.coeffs[k])(y,t)*matrices[k] for k in matrices.keys()], axis=0)

        else:
            dim = next(i for i,x in enumerate(self.dimensions["category"]) if x==dimensions[0])
            return lambda y, t: np.sum([self.make_callable(self.coeffs[k])(y,t)*matrices[k][dim,:] for k in matrices.keys()], axis=0)

    def r0(self):
        beta = np.diag(self.params["beta"])

        pm = self.params["proba_mild"]
        ps = self.params["proba_severe"]
        pa = 1 - pm - ps
        gra = 1/self.params["recovery_duration_asymptomatic"]
        grm = 1/self.params["recovery_duration_mild"]
        grs = (1-self.params["proba_icu"])*1/self.params["symptoms_to_hospital_duration"] + self.params["proba_icu"]*1/self.params["symptoms_to_icu_duration"]
        g = np.diag(pa/gra + self.params["symptomatic_isolation"]*pm/grm + self.params["symptomatic_isolation"]*ps/grs)

        vals = np.linalg.eigvals(g @ self.contact_matrix("all")(None, 0) @ beta)

        return np.max(vals)
