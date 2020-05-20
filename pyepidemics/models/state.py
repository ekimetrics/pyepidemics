
import pandas as pd



class State(pd.Series):
    def __init__(self,data):
        super().__init__(data)
        
    def __getitem__(self,key):
        if key in self.index:
            return self.loc[key]
        else:
            states = [x.split("_")[0] == key for x in self.index]
            return self.loc[states].values
