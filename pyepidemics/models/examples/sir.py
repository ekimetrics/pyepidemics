from ..model import CompartmentalModel


class SIR(CompartmentalModel):
    def __init__(self,N:int,beta:float,gamma:float):
        """Classical SIR Model

        Args:
            N (int): Population considered
            beta (float): How many person each person infects per day
            gamma (float): Rate of infection, ie duration = 1/gamma
        """
        
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


    def R0(self) -> float:
        """Computes the reproduction factor of the model aka the R0

        Returns:
            float: Computed R0
        """
        return self.beta/self.gamma

