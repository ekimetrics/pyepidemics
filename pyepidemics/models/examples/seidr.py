"""Simple SEIDR Model
Inspiration from towardsdatascience.com/infectious-disease-modelling-beyond-the-basic-sir-model-216369c584c4
"""

from ..model import CompartmentalModel


class SEIDR(CompartmentalModel):
    def __init__(self,N,beta,delta,gamma,rho,alpha):

        # Define compartments name and number
        compartments = ["S","E","I","D","R"]
        super().__init__(compartments)

        # Parameters
        self.N = N # Total population
        self.beta = beta # How many person each person infects per day
        self.gamma = gamma # Rate of infection, duration = 1/gamma
        self.delta = delta # Incubation period = 1/delta
        self.rho = rho # How many days to die = 1/rho
        self.alpha = alpha # Probability to die

        # Add transition
        self.add_transition("S","E",lambda y,t: y["S"]/self.N * self.beta * y["I"])
        self.add_transition("E","I",lambda y,t: self.delta * y["E"])
        self.add_transition("I","R",lambda y,t : self.gamma * (1 - self.alpha) * y["I"])
        self.add_transition("I","D",lambda y,t : self.rho * self.alpha * y["I"])
