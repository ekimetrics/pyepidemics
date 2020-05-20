from ..model import CompartmentalModel

class GranularSIR(CompartmentalModel):
    
    def __init__(self,params,dimensions,contact = None):

        super().__init__(["S","I","R"],params = params,dimensions = dimensions)

        self.N = params["N"].sum()
        self.prepare_contact_matrix(contact)
    
        def StoI(dimensions):
            beta,N,I,S = self.get(["beta","N","I","S"],dimensions)
            C = self.get_contact_vector(dimensions)
            return lambda y,t: beta *  (y[S] / N) * C.dot(y["I"])

        def ItoR(dimensions):
            gamma,I = self.get(["gamma","I"],dimensions)
            return lambda y,t: gamma * y[I]


        self.add_transition("S","I",StoI,granularity=True)
        self.add_transition("I","R",ItoR,granularity=True)
