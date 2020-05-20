"""Simple SEIR Model
Inspiration from towardsdatascience.com/infectious-disease-modelling-beyond-the-basic-sir-model-216369c584c4
"""

from ..model import CompartmentalModel


class SEIR(CompartmentalModel):
    def __init__(self,N,beta,delta,gamma):

        # Define compartments name and number
        compartments = ["S","E","I","R"]
        super().__init__(compartments)

        # Parameters
        self.N = N # Total population
        self.beta = beta # How many person each person infects per day
        self.gamma = gamma # Rate of infection, duration = 1/gamma
        self.delta = delta # Incubation period = 1/delta

        # Add transitions
        self.add_transition("S","E",lambda y,t: self.beta * y["I"] * y["S"]/self.N)
        self.add_transition("E","I",lambda y,t: self.delta * y["E"])
        self.add_transition("I","R",lambda y,t: self.gamma * y["I"])

