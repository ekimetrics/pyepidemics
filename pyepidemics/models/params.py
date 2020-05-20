
import pandas as pd


"""
TODO
- Add body signature in the lambda function with inspect.getsource
"""

class Params(pd.DataFrame):
    def __init__(self,**kwargs):

        # Store 
        self._metadata = kwargs
        index = pd.MultiIndex.from_product(self.dimensions.values(), names=self.dimensions.keys())
        super().__init__(index = index)


    @property
    def dimensions(self):
        return self._metadata


    def add(self,value,name = None,level = None):
    
        if isinstance(value,dict):

            for name,value in value.items():
                self.add(value,name)
        else:

            if level is None:
                self[name] = value

            else:
                assert level in self.dimensions.keys()
                
                # Convert value to dataframe
                if isinstance(value,list):
                    value = pd.DataFrame(value,columns = [name],index = self.dimensions[level])
                elif isinstance(value,dict):
                    value = pd.DataFrame(value,columns = [name])
                elif isinstance(value,pd.DataFrame):
                    assert all([x in self.dimensions[level] for x in value.index])
                else:
                    raise Exception("Params must be dict, list or DataFrame")

                # Rename index for merge
                value.index.name = level

                # Merge on multiindex
                super().__init__(self.join(value))


    def get_param(self,name,dimensions):
        return self.loc[tuple(dimensions),name]

    def get_params_for(self,**kwargs):
        # Use xs
        # Maybe Deprecated
        k,v = list(kwargs.items())[0]

        if len(self.index.names) > 1:
            return self.xs(v,level=k)
        else:
            return self.loc[v]

        
