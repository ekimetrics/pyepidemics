import sys

def ipython_info():
    ip = False
    if 'ipykernel' in sys.modules:
        ip = 'notebook'
    elif 'IPython' in sys.modules:
        ip = 'terminal'
    return ip

import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from scipy.integrate import odeint
if ipython_info() == "notebook":
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm

# Custom library
from .state import State
from .states import CompartmentStates
from .network import CompartmentNetwork
from ..params.metrics import custom_loss
from ..params.optimizer import ParamsOptimizer
from ..policies.utils import multiple_sigmoid_response
            


class CompartmentalModel:


    def __init__(self,compartments,params = None,dimensions = None,offset = None,I0 = 1,start_state = None,start_date = None):

        self._states = compartments
        self._dimensions = dimensions
        self._offset = offset
        self._I0 = I0
        self._start_state = start_state
        self._start_date = start_date
        self.params = params

        assert self._start_state in self._states



        if self._dimensions is not None:
            assert isinstance(self._dimensions,dict)
            self._compartments = ["_".join(x) for x in itertools.product(self.states,*self.dimensions.values())]

        else:
            self._compartments = self.states

        self.network = CompartmentNetwork(self.compartments)

    @property
    def offset(self):
        if self._offset is None:
            return 0
        else:
            return int(self._offset)

    @property
    def I0(self):
        return self._I0


    @property
    def start_state(self):
        return self._start_state

    
    @property
    def start_date(self):
        return self._start_date


    @property
    def states(self):
        return self._states

    @property
    def granularity(self):
        if self._dimensions is None:
            return None
        else:
            return list(self.dimensions.keys())

    @property
    def dimensions_product(self):
        return list(itertools.product(*self.dimensions.values()))

    @property
    def dimensions(self):
        if self._dimensions is None:
            return {}
        else:
            return self._dimensions


    @property
    def compartments(self):
        return self._compartments


    @property
    def compartments_index(self):
        return pd.MultiIndex.from_product(self.states,*self.dimensions.values())


    @staticmethod
    def make_callable(value):   
        if callable(value):
            return value

        elif isinstance(value, dict):
            assert "dates" in value.keys() and "values" in value.keys(), "You provided a dictionnary as values, it shouldhave two keys: dates and values"
            return lambda y,t : value["values"][next(i for i,x in enumerate(value["dates"] + [np.infty]) if x>=t)-1]
        
        else:
            return lambda y,t : value

    
    def solve(self,n_days = 100,init_state = None,start_date = None):
        """Main ODE solver function to predict future population values in each compartments
        The function will use the network created by transitions between compartments
            - Derivatives are computed using transitions 
            - ODE system is integrated using scipy odeint solver
        
        Args:
            init_state (dict, list, tuple, numpy array): the first value to initialize the solver, ie init population
            n_days (int): number of days on which to run the solver, ie prediction horizon
            start_date (str or datetime): use real dates instead of just number of days

        Returns:
            states (States) - a custom pd.DataFrame with population by compartment over time
        """

        # If init state is not given we use I0
        if init_state is None:
            assert self.start_state is not None
            init_state = int(self.I0)

        # Transform init_state into state object
        init_state = self.make_state(init_state)

        # Safety checks
        tol = 2
        assert hasattr(self,"compartments")
        assert len(init_state) == len(self.compartments)
        assert hasattr(self,"N")
        assert np.abs(init_state.sum() - self.N) < tol,f"Init state {init_state.values} does not sum to total population {self.N}"
        assert n_days > self.offset
 
        # Grid of time points (in days)
        # Take offset into account
        offset = self.offset
        t = np.linspace(0, n_days - offset, n_days - offset +1)

        # Integrate the model equations over the time grid, t.
        states = odeint(self.derivative, init_state, t)

        # Converts to DataFrame and then to custom object
        states = pd.DataFrame(states,columns = self.compartments)

        # Add offset into account
        if offset > 0:
            states.index = range(offset,n_days + 1)
            states = states.reindex(range(0,n_days + 1))
            states = states.fillna(method = "bfill")
        elif offset < 0:
            states.index = [x + offset for x in states.index]

        # Convert to custom object
        states = CompartmentStates(states)
        states.build_aggregates(self.states)

        # If start date is given, convert to dates
        if self.start_date is not None:
            start_date = self.start_date
        if start_date is not None:
            index = pd.to_datetime(start_date) + pd.TimedeltaIndex(states.index,unit = "D")
            states.index = index
            
        return states


    def make_state(self,y):
        """Helper function to create a State object for easy manipulation
        States object are extension of Pandas Series with additions to easily extract vectors by category instead of just values
        It serves basically as a multi index when you have states by granularity
        This function will transform input y into this state of object from various input types : 
            - arrays as list, tuple, or numpy arrays
            - dict 
        
        For example: y["I"] will return a vector y.loc[["I_young","I_adult","I_senior"]] if we have age categories ["young","adult","old]
        """

        # Create state object from array
        if isinstance(y,tuple) or isinstance(y,list) or isinstance(y,np.ndarray):
            y = State({self.compartments[i]:value for i,value in enumerate(y)})

        # Create state object from dict and initalize other values with 0 if not in the dict
        elif isinstance(y,dict):

            y = State({c:y.get(c,0) for c in self.compartments})

        # Special case where we initialize one state in the second compartment and the rest in the first
        elif isinstance(y,int):
            start_state = self.compartments[1] if self.start_state is None else self.start_state
            y = self.make_init_state(self.compartments[0],(start_state,y))
            y = self.make_state(y)

        # Custom exception
        else:
            raise Exception("Dtype of state vector y is not recognized among tuple,list,ndarray,dict,int")

        return y


    def make_init_state(self,state,start_case = None):
        """Helper function to prepare the first state dictionary to be fed to the ODE solver
        Indeed when you have a lot of categories and compartment it can be a hassle to iterate and experiment
        Here it initialize the population on a given state, most of the time "S" (by category if there is a granularity)
        And we substract the first cases in the propagation using start_case. 

        For example: 
            - state = "S" and start_case = ("E",1) will create the init state dict {"S": N - 1,"E" : 1} in a SEIR model
            - state = "S" and start_case = ("E_young",1) will create the init state dict {"S_young":N/2 - 1,"S_old" : N/2,"E_young":1}
        """
        # Init state dict
        d = {}

        # Init first population values in the first state
        if self.granularity is not None:
            for dimensions in self.dimensions_product:
                N,s = self.get(["N",state],dimensions)
                d[s] = N
        else:
            d[state] = self.N
            
        # Start the propagation with the first case
        if start_case is not None:

            # If there is a granularity (age / region)
            if self.granularity is not None:

                # If input is a tuple (only case in one category)
                if isinstance(start_case,tuple):
                    assert len(start_case) == 2
                    start_state,value = start_case
                    modified_state = f"{state}_{start_state.split('_',1)[1]}"
                    d[modified_state] -= value
                    d[start_state] = value

                # If input is a list of tuples (cases in several categories)
                elif isinstance(start_case,list):
                    for case in start_case:
                        assert len(case) == 2
                        start_state,value = case
                        modified_state = f"{state}_{start_state.split('_',1)[1]}"
                        d[modified_state] -= value
                        d[start_state] = value

            # Without granularity
            else:
                assert isinstance(start_case,tuple)
                assert len(start_case) == 2
                start_state,value = start_case
                d[state] -= value
                d[start_state] = value

        return d

    def derivative(self,y,t):

        # Transform init_state into state object
        # This is already done in .solve() method but scipy odeint convert it to numpy array
        y = self.make_state(y)

        # Compute derivatives via network
        dydt = self.network.compute_derivatives(self.compartments,y,t)

        return dydt


    def add_transition(self,start,end,transition,granularity = False):

        if self.granularity is None or granularity == False:
            self.network.add_transition(start,end,transition)
        else:
            assert self.granularity is not None
            
            # Iterate on levels of the granularity (for example region or age)
            for dimensions in self.dimensions_product:
                start_node = self.get(start,dimensions)
                end_node = self.get(end,dimensions)
                transition_fn = transition(dimensions)
                self.network.add_transition(start_node,end_node,transition_fn)


    def add_transitions(self,transitions,granularity = False):

        if self.granularity is None or granularity == False:
            assert isinstance(transitions,dict)

            for start,d in transitions.items():
                for end,transition in d.items():
                    self.network.add_transition(start,end,transition)

        else:
            assert self.granularity is not None
            for dimensions in self.dimensions_product:
                transitions_dict = transitions(dimensions)
            
                for start,d in transitions_dict.items():
                    for end,transition in d.items():
                        start_node = self.get(start,dimensions)
                        end_node = self.get(end,dimensions)
                        self.network.add_transition(start_node,end_node,transition)
    

    def show_network(self,**kwargs):
        self.network.show(**kwargs)


    def get_param(self,name,dimensions):
        return self.params.get_param(name,dimensions)

    def get_compartment(self,name,dimensions):
        return f"{name}_{'_'.join(dimensions)}"


    def get(self,name,dimensions):

        if isinstance(name,list):
            return [self.get(n,dimensions) for n in name]
        else:
            if name in self.params.columns:
                return self.get_param(name,dimensions)
            elif name in self.states:
                return self.get_compartment(name,dimensions)
            else:
                raise Exception(f"Name {name} for dimensions {dimensions} should be either in params or a state")



    def prepare_contact_matrix(self,contact):


        if contact is not None:
            # Safety checks
            assert isinstance(contact,dict)
            assert self.granularity is not None
            assert all([key in self.granularity for key in contact])
        else:
            contact = {}


        # Matrix as dataframes
        matrices_np = []
        for key in self.granularity:

            # Prepare individual matrix index and shape
            index = self.dimensions[key]

            # If there is a contact matrix
            # If there is not we suppose no contact ie, identity matrix
            matrix = contact[key] if key in contact else np.identity(len(index))
            
            # Convert to numpy if not the case and add to list and dictionary
            if not isinstance(matrix,np.ndarray): matrix = np.array(matrix)
            matrices_np.append(matrix)
            contact[key] = pd.DataFrame(matrix,index = index,columns = index)

        if len(matrices_np) > 1:
    
            # Create master matrix
            dim = np.product([len(x) for x in matrices_np])
            shape = (dim,dim)
            matrix = np.multiply.outer(*matrices_np).swapaxes(1,2).reshape(*shape)
            index = ["_".join(x) for x in self.dimensions_product]
            matrix = pd.DataFrame(matrix,index = index,columns = index)
            contact["all"] = matrix

        else:
            contact["all"] = contact[key].copy()

        # Store as attribute
        self.contact = contact


    def get_contact_vector(self,dimensions):
        key = "_".join(dimensions)
        return self.contact["all"].loc[key].values





    #==================================================================================
    # PARAMS OPTIMIZATION
    #==================================================================================



    def reset(self,params):
        raise Exception("No reset function is implemented, if you want to use optimizer, write a custom reset function")



    def objective(self,true,params,init_state = None,constraint = None,return_dict = False):

        # Reset model with params
        # Exception will be raised if no custom reset function is implemented
        self.reset(params)

        # Make prediction
        states = self.predict(true,init_state = init_state)

        # Compute and return loss
        cols = true.columns.tolist()
        loss,loss_dict = custom_loss(states.loc[true.index],true,cols = cols)

        if constraint is not None:
            loss = constraint(self,loss) 

        if not return_dict:
            return loss
        else:
            return loss_dict



    def fit(self,true,space,init_state = None,n = 100,**kwargs):

        # Initialize optimizer
        self.opt = ParamsOptimizer(self)

        # Run optimizer
        best = self.opt.run(true,space,init_state = init_state,n=n,**kwargs)

        # Reset with best parameters
        self.reset(best)


    def predict(self,true,init_state = None,forecast_days = 0):

        # Prepare temporal variables
        start_date = true.index[0]
        n_days = len(true) - 1 + forecast_days

        # Make prediction using model
        states = self.solve(init_state = init_state,start_date = start_date,n_days = n_days)
        return states

    
    def predict_interval(self,true,init_state,forecast_days = 0,n = 100,q = 0.25,norm_fit = False):

        all_params = self.opt.sample_params(n = n,q = q,norm_fit = norm_fit)
        all_states = []

        for i,params in enumerate(tqdm(all_params)):

            self.reset(params)

            states = self.predict(true,init_state,forecast_days)
            states["sample"] = i
            all_states.append(states) 

        all_states = pd.concat(all_states).reset_index().set_index(["index","sample"]).unstack("sample")
        
        return all_states



    def show_prediction_interval(self,true,init_state,forecast_days = 0,n = 100,q = 0.25,figsize = (15,4),only_pred = False):

        pred = self.predict_interval(true,init_state,forecast_days,n,q)
        pred_max = pred.max(axis = 1,level = 0)
        pred_min = pred.min(axis = 1,level = 0)
        pred_mean = pred.mean(axis = 1,level = 0)   

        if only_pred:
            pred_min.iloc[:-forecast_days] = pred_mean.iloc[:-forecast_days]
            pred_max.iloc[:-forecast_days] = pred_mean.iloc[:-forecast_days]

        # Create columns
        cols = true.columns.tolist()

        # Compare prediction for each columns
        for col in cols:

            pred_mean[col].plot(figsize = figsize,label = "pred",title = f"Prediction for compartment ({col}) against real values")
            plt.fill_between(pred_max.index,pred_min[col],pred_max[col],alpha = 0.1)
            true[col].plot(style=".",c = "black",label = "true")
            plt.legend()
            plt.show()




    def show_prediction(self,true,init_state = None,forecast_days = 0,pred = None,log_y = False,secondary_y = False,figsize = (15,4),save = False,filename = None):

        # Create columns
        cols = true.columns.tolist()

        # Make prediction
        if pred is None:
            pred = self.predict(true,init_state,forecast_days)

        # Compare prediction for each columns
        for col in cols:

            series_pred = pred[col]
            if log_y:
                series_pred = series_pred.astype(int)

            series_pred.plot(figsize = figsize,label = "pred",logy = log_y,title = f"Prediction for compartment ({col}) against real values")
            true[col].plot(style=".",c = "black",label = "true",secondary_y = secondary_y,logy = log_y)
            plt.legend()
            if save:
                if filename is None:
                    new_filename = f"prediction_{col}_{str(int(time.time()))}.png"
                else:
                    new_filename = filename.replace(".png",f"_{col}.png")
                plt.savefig(new_filename)
            plt.show()



    def _make_beta_parameter(self,beta,default_duration = 4):
    
        # Create lockdown variable, ie: simply beta varying over time
        # Example beta = [3.5,[0.9,3.5],[10,20]]
        if isinstance(beta,list):
            assert len(beta) in [3,4]

            # Split beta to take
            beta_start = beta[0]
            beta_values = beta[1]
            beta_dates = beta[2]
            if len(beta) == 4:
                beta_transitions = beta[3]
            else:
                beta_transitions = default_duration

            # Safety checks
            assert isinstance(beta_start,float) or isinstance(beta_start,int)
            assert isinstance(beta_values,list) and isinstance(beta_dates,list)
            assert len(beta_values) == len(beta_dates)

            # Create multiple sigmoid response
            beta = lambda y,t : multiple_sigmoid_response(t,beta_start,beta_values,beta_dates,beta_transitions)

        # Make callable
        return self.make_callable(beta)
