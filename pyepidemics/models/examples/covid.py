"""Custom COVID19 Compartmental model
"""

from ..model import CompartmentalModel


class COVID19(CompartmentalModel):
    def __init__(self,
            N,
            beta,
            incubation_rate = 1/3.7,               
            recovery_rate_asymptomatic = 1/4.7,
            recovery_rate_mild = 1/4.7,
            symptoms_to_hospital_rate = 1/5.5,
            symptoms_to_icu_rate = 1/7,
            proba_severe = 0.071,
            proba_asymptomatic = 0.2,
            proba_icu = 0.182,
            recovery_rate_hospital = 0.046,
            recovery_rate_icu = 0.035,
            death_rate_hospital = 0.0046,
            death_rate_icu = 0.0087,
            isolation_ratio = 0.25,
            offset = None,
    ):
        """COVID19 Compartmental Model

        Parameters:
        Default params are set according to INSERM research paper
        """

        params = {
            "N":N,
            "beta":beta,
            "incubation_rate":incubation_rate,               
            "recovery_rate_asymptomatic":recovery_rate_asymptomatic,
            "recovery_rate_mild":recovery_rate_mild,
            "recovery_rate_hospital":recovery_rate_hospital,
            "recovery_rate_icu":recovery_rate_icu,
            "symptoms_to_icu_rate":symptoms_to_icu_rate,
            "symptoms_to_hospital_rate":symptoms_to_hospital_rate,
            "death_rate_hospital":death_rate_hospital,
            "death_rate_icu":death_rate_icu,
            "proba_severe":proba_severe,
            "proba_asymptomatic":proba_asymptomatic,
            "proba_icu":proba_icu,
            "isolation_ratio":isolation_ratio,
        }

        # Define compartments name and number
        compartments = ["S","E","Ia","Im","Is","H","ICU","D","R"]
        super().__init__(compartments,offset = offset,params = params)

        # Parameters
        self.N = N
        self.beta = self._make_beta_parameter(beta)


        # Prepare transitions
        transitions = {
            "S":{
                "E":lambda y,t : y["S"] / N * self.beta(y,t) * (y["Ia"]+ isolation_ratio * (y["Im"] + y["Is"]))
            },
            "E":{
                "Ia":lambda y,t : incubation_rate * (proba_asymptomatic) * y["E"],
                "Im":lambda y,t : incubation_rate * (1 - proba_asymptomatic - proba_severe) * y["E"],
                "Is":lambda y,t : incubation_rate * (proba_severe) * y["E"],
            },
            "Ia":{
                "R":lambda y,t : recovery_rate_asymptomatic * y["Ia"],
            },
            "Im":{
                "R":lambda y,t : recovery_rate_hospital* y["Im"],
            },
            "Is":{
                "ICU":lambda y,t : symptoms_to_icu_rate * (proba_icu) * y["Is"],
                "H":lambda y,t : symptoms_to_icu_rate * (1-proba_icu) * y["Is"],
            },
            "ICU":{
                "R":lambda y,t : recovery_rate_icu * y["ICU"],
                "D":lambda y,t : death_rate_icu * y["ICU"],
            },
            "H":{
                "R":lambda y,t : recovery_rate_hospital * y["H"],
                "D":lambda y,t : death_rate_hospital * y["H"],
            },
        }


        # Add transition
        self.add_transitions(transitions)

    def r0(self, beta):
        pa = self.params["proba_asymptomatic"]
        ps = self.params["proba_severe"]
        proba_icu = self.params["proba_icu"]
        recovery_rate_asymptomatic = self.params["recovery_rate_asymptomatic"]
        recovery_rate_mild = self.params["recovery_rate_mild"]
        recovery_rate_severe = (1-proba_icu) * self.params["symptoms_to_hospital_rate"] + proba_icu * self.params["symptoms_to_icu_rate"]
        isolation_ratio = self.params["isolation_ratio"]

        return beta * (pa / recovery_rate_asymptomatic + (isolation_ratio * (1-pa-ps) / recovery_rate_mild) + (isolation_ratio * ps / recovery_rate_severe))
