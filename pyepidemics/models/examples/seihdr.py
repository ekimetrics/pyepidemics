"""Simple SEIHDR Model
Inspiration from towardsdatascience.com/infectious-disease-modelling-beyond-the-basic-sir-model-216369c584c4
"""

from ..model import CompartmentalModel


class SEIHDR(CompartmentalModel):
    def __init__(self,N,beta,delta,gamma,rho,alpha,theta,phi,kappa):

        # Define compartments name and number
        compartments = ["S","E","I","H","D","R"]
        super().__init__(compartments)

        # Parameters
        self.N = N # Total population
        self.beta = self.make_callable(beta) # How many person each person infects per day
        self.gamma = self.make_callable(gamma) # Recovery rate at the hospital, duration = 1/gamma
        self.delta = self.make_callable(delta) # Incubation period = 1/delta
        self.phi = self.make_callable(phi) # Probability for the complications and go to the hospital
        self.theta = self.make_callable(theta) # How long for the complications 
        self.kappa = self.make_callable(kappa) # How long for the symptoms to disappear without going to a hospital
        self.rho = self.make_callable(rho) # How many days to die = 1/rho
        self.alpha = self.make_callable(alpha) # Probability to die in the hospital

        # Add transition
        self.add_transition("S","E",lambda y,t: y["S"] / N * self.beta(y,t) * y["I"])
        self.add_transition("E","I",lambda y,t: self.delta(y,t) * y["E"])
        self.add_transition("I","H",lambda y,t: self.theta(y,t) * self.phi(y,t) * y["I"])
        self.add_transition("I","R",lambda y,t : self.kappa(y,t) * (1 - self.phi(y,t)) * y["I"])
        self.add_transition("H","R",lambda y,t : self.gamma(y,t) * (1 - self.alpha(y,t)) * y["H"])
        self.add_transition("H","D",lambda y,t : self.rho(y,t) * self.alpha(y,t) * y["H"])
