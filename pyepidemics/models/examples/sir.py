"""Simple SIR Model
Inspiration from towardsdatascience.com/infectious-disease-modelling-beyond-the-basic-sir-model-216369c584c4
"""


from ..model import CompartmentalModel


class SIR(CompartmentalModel):
    def __init__(self,N,beta,gamma):
        
        # Define compartments name and number
        compartments = ["S","I","R"]
        super().__init__(compartments)

        # Parameters
        self.N = N # Total population
        self.beta = beta # How many person each person infects per day
        self.gamma = gamma # Rate of infection, duration = 1/gamma
        
        # Add transition
        self.add_transition("S","I",lambda y,t: self.beta * y["S"] * y["I"] / self.N)
        self.add_transition("I","R",lambda y,t: self.gamma * y["I"])

