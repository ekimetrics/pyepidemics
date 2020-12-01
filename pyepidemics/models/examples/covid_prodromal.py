from ..model import CompartmentalModel


class COVID19Prodromal(CompartmentalModel):
    def __init__(self,
            N,
            beta,
            incubation_rate = 1/3.7,
            prodromal_rate = 1/1.5,   
            recovery_rate_asymptomatic = 1/3.2,
            recovery_rate_mild = 1/3.2,
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
            I0 = 1,
            **kwargs,
    ):
        """COVID19 Compartmental Model

        Parameters:
        Default params are set according to INSERM research paper
        """

        params = {
            "N":N,
            "beta":beta,
            "incubation_rate":incubation_rate,
            "prodromal_rate":prodromal_rate,           
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
        compartments = ["S","E","Ip","Ia","Im","Is","H","ICU","D","R"]
        start_state = "Ip"
        super().__init__(compartments,I0 = I0,start_state = start_state,params = params)

        # Parameters
        self.N = N
        self.beta = self._make_beta_parameter(beta)
        self.isolation_ratio = self._make_beta_parameter(isolation_ratio)


        # Prepare transitions
        transitions = {
            "S":{
                "E":lambda y,t : y["S"] / N * self.beta(y,t) * (y["Ip"] + y["Ia"] + self.isolation_ratio(y,t) * (y["Im"] + y["Is"]))
            },
            "E":{
                "Ip":lambda y,t: incubation_rate * y["E"],
            },
            "Ip":{
                "Ia":lambda y,t : prodromal_rate * (proba_asymptomatic) * y["Ip"],
                "Im":lambda y,t : prodromal_rate * (1 - proba_asymptomatic - proba_severe) * y["Ip"],
                "Is":lambda y,t : prodromal_rate * (proba_severe) * y["Ip"],
            },
            "Ia":{
                "R":lambda y,t : recovery_rate_asymptomatic * y["Ia"],
            },
            "Im":{
                "R":lambda y,t : recovery_rate_hospital* y["Im"],
            },
            "Is":{
                "ICU":lambda y,t : symptoms_to_icu_rate * (proba_icu) * y["Is"],
                "H":lambda y,t : symptoms_to_hospital_rate * (1-proba_icu) * y["Is"],
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

    def R0(self,beta,isolation_ratio = None):
        gamma = self.get_gamma(isolation_ratio)
        return beta / gamma


    def get_gamma(self,isolation_ratio = None):

        # Prepare probabilities
        pa = self.params["proba_asymptomatic"]
        ps = self.params["proba_severe"]
        proba_icu = self.params["proba_icu"]

        # Prepare rates
        rate_asymptomatic = self.params["recovery_rate_asymptomatic"]
        rate_mild = self.params["recovery_rate_mild"]
        rate_severe = (1-proba_icu) * self.params["symptoms_to_hospital_rate"] + proba_icu * self.params["symptoms_to_icu_rate"]
        rate_prodromal = self.params["prodromal_rate"]
        if isolation_ratio is None:
            isolation_ratio = self.params["isolation_ratio"]

        return 1 / (
            1 / rate_prodromal + \
            pa / rate_asymptomatic + \
            (isolation_ratio * (1-pa-ps) / rate_mild) + \
            (isolation_ratio * ps / rate_severe) \
        )
