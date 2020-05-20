import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

plt.style.use("bmh")
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['axes.grid'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False

class CompartmentStates(pd.DataFrame):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        # Store total population
        self._N = int(self.sum(axis = 1).iloc[0])


    @property
    def N(self):
        return self._N


    def __getitem__(self, key):

        if isinstance(key,str):
            if key not in self.columns:
                cols = [col for col in self.columns if (key in col.split("_") or ("_" in key and key in col))]
                print(cols)

                # Raise KeyError if no match
                if len(cols) == 0:
                    raise KeyError(f"Key {key} is missing from States DataFrame object")
                else:
                    key = cols
            

        df = super().__getitem__(key)
        if isinstance(df,pd.Series):
            return df
        return CompartmentStates(df)

    def build_aggregates(self, states):
        """Build aggregated variables accros compartments if needed
        """
        for state in states:
            if len([name for name in self.columns if name.startswith(state)]):
                self[state] = self[[name for name in self.columns if name.startswith(state)]].sum(1)

    def _melt(self,states = None, group = None,date=False):

        if states is None:
            states = self
            
        if date:
            states.index = [
                datetime.date(2020, 3, 17) + datetime.timedelta(days=x)
                for x in range(len(states))]

        states = (states
            .reset_index()
            .rename(columns = {"index":"days"})
            .melt(id_vars = "days")
            .rename(columns = {"variable":"compartment"})
        )

        if group is not None:
            assert isinstance(group,dict)
            group = pd.Series(group,name = "compartment").explode().reset_index().rename(columns = {"index":"facet"})
            states = states.merge(group,on="compartment")

        return states



    def _normalize(self):
        return self.divide(self.sum(axis = 1),axis = 0) * 100


    def show(self,figsize = (15,4),plotly = True,show = True, return_plot=False,group = None,facet_row = None,facet_col = None,facet_col_wrap=5,**kwargs):

        if plotly:
            states_plotly = self._melt(group = group)

            if group is None:
                fig = px.line(states_plotly,x = "days",y = "value",line_group="compartment",color="compartment",
                    facet_row = facet_row,
                    facet_col = facet_col,
                **kwargs)
            else:
                fig = px.line(states_plotly,x = "days",y = "value",line_group="compartment",color="compartment",facet_row = "facet")

            fig.update_yaxes(matches=None)
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            

            if return_plot:
                return fig
            else:
                fig.show()
        else:
            # Plot with matplotlib
            self.plot(figsize = figsize)
            if show: 
                plt.show()


    def show_evolution_norm(self,figsize = (15,4),plotly = True,show = True, return_plot=False):

        # Compute proportion
        states_norm = self._normalize()

        if plotly:
            states_plotly = self._melt(states_norm)
            fig = px.area(states_plotly,x = "days",y = "value",line_group="compartment",color="compartment")
            if return_plot:
                return fig
            else:
                fig.show()
        else:
            # Plot
            if show:
                states_norm.plot(kind = "area",figsize = figsize)
                plt.show()


    def explore(self,plotly = True):
        self.show(plotly = plotly)
        self.show_evolution_norm(plotly = plotly)

    def show_peak(self,state = "I",figsize = (15,4),show = True, plotly=False, **kwargs):
        
        peak = self.find_peak(state)

        # Plot with matplotlib
        if not plotly:
            self.show(figsize=figsize, plotly=plotly, show=False, **kwargs)
            plt.axvline(x=peak,lw = 1,color = "black",linestyle="--")
            plt.text(peak+0.5,0,f"{peak} days",rotation=0)

            if show:
                plt.show()
        else:
            return self.show(figsize=figsize, plotly=True, show=False, return_plot=True, **kwargs)

    def find_peak(self,state = "I"):
        peak = self[state].idxmax()
        return peak
