import sys

def ipython_info():
    ip = False
    if 'ipykernel' in sys.modules:
        ip = 'notebook'
    elif 'IPython' in sys.modules:
        ip = 'terminal'
    return ip

import pandas as pd
import matplotlib.pyplot as plt

if ipython_info() == "notebook":
    from tqdm import tqdm_notebook as tqdm
else:
    from tqdm import tqdm

from scipy.stats import norm
import yaml
import time

# Optuna imports
import optuna
from optuna.pruners import SuccessiveHalvingPruner
from optuna.pruners import HyperbandPruner
from optuna.samplers import TPESampler
from optuna import visualization


class EarlyStoppingError(Exception):
    count = 0



class ParamsOptimizer:
    def __init__(self,model):

        # Store model as attribute
        self.model = model


    @staticmethod
    def _sample_param(trial,key,value):
        if isinstance(value,tuple) and len(value) == 2:
            return trial.suggest_uniform(key,value[0],value[1])
        elif isinstance(value,dict):
            return trial.suggest_normal(key,value["mu"],value["sigma"]),
        else:
            return Exception(f"Space {key} for optimization is not recognized {value}, should be tuple or dict")


    def _sample(self,trial,space):
        params = {}
        for key,value in space.items():
            params[key] = self._sample_param(trial,key,value)
        return params


    def save_params(self,filename = None,message = None,info = None):

        if filename is None:
            filename = f"calibration_params_{str(int(time.time()))}.yaml"
        if info is None:
            info = {}
        
        def clean_dict(x):
            def clean_float(y):
                try:
                    return float(y)
                except:
                    return y
            return {k:clean_float(v) for k,v in x.items()}

        d = {
            "calibrated_params":self.study.best_params,
            "info":{
                "date":str(pd.to_datetime("today")),
                "message":None,
                **info
            }
        }


        if hasattr(self.model,"params"):
            d["default_params"] = clean_dict({k:v for k,v in self.model.params.items() if k not in self.study.best_params})

        with open(filename,"w") as file:
            yaml.dump(d,file)
            print(f"... Parameters saved in yaml file {filename}")


    def run(self,true,space,init_state,objective_fn = None,n = 100,
        early_stopping = None,
        timeout = None,
        constraint = None,
        callbacks = None,
        show_progress_bar = True,
        n_jobs = 1,
        info = None,
        save = True,
        filename = None,
    ):

        # Verify n_jobs is equal to 1
        assert n_jobs == 1, f"Parallel optimization is not implemented yet"

        # Disable default logging of Optuna
        optuna.logging.disable_default_handler()

        # Prepare Optuna objective function
        if objective_fn is None:
            objective_fn = lambda params : self.model.objective(true,params,init_state,constraint = constraint)
        def objective(trial):
            params = self._sample(trial,space)
            return objective_fn(params)

        # Create Optuna study
        # Possibility here to change sampler and pruner
        sampler = TPESampler()
        pruner = HyperbandPruner()
        self.study = optuna.create_study(direction= "minimize",pruner=SuccessiveHalvingPruner(),sampler = TPESampler())

        # Create callback
        pbar = tqdm(range(0,n),desc = "Parameters Optimization")
        def custom_callback(study,trial):
            # Message
            pbar.set_postfix({"value":trial.value,"best_value":study.best_value})
            pbar.update()
            # Early stopping
            if early_stopping is not None:
                if trial.number - study.best_trial.number > early_stopping:
                    raise EarlyStoppingError("Stopping")
            

        # Run optimizer to find best parameters
        # Try except block allow for early stopping if best value has not changed since a given number of trials
        try:
            if callbacks is None: callbacks = []

            self.study.optimize(
                objective,
                n_trials = n,
                n_jobs = n_jobs,
                show_progress_bar = False,
                timeout = timeout,
                gc_after_trial = False, # is it accelerating computation ?
                callbacks = [custom_callback] + callbacks
            )

        except EarlyStoppingError:
            print(f"... Early stopping - best value has not changed since {early_stopping} trials at {self.study.best_value}")

        # Return best value
        best = self.study.best_params
        print(f"... Found best solution {best} for value {self.study.best_value}")

        # Compute final loss
        loss_dict = self.model.objective(true,best,init_state,return_dict = True)
        if info is None:
            info = {}

        # Save parameters
        if save:
            self.save_params(filename,message = "Parameters calibration",info = {
                "on":true.columns.tolist(),
                "init_state":init_state,
                **loss_dict,
                **info
            })

        return best


    def show_contour(self,params = None):
        return visualization.plot_contour(self.study,params = params)


    def show_parallel_coordinates(self,params = None):
        return visualization.plot_parallel_coordinate(self.study,params = params)


    def show_history(self):
        return visualization.plot_optimization_history(self.study)


    def show_params(self,params = None):
        return visualization.plot_slice(self.study,params = params)




    def estimate_params_distributions(self,q = 0.05,return_df = False,summary = False):

        params = {}

        # Prepare params dataframe by filter on quantile
        params_df = self.study.trials_dataframe()
        value_quantile = params_df["value"].quantile(q = q)
        params_df = params_df.query(f"value < {value_quantile}")

        # Select only parameters
        params_df = params_df[[x for x in params_df.columns if (x.startswith("params") or x == "value")]]
        params_df.columns = [x.replace("params_","") for x in params_df.columns]
        params_df = params_df.sort_values("value")

        if return_df:
            return params_df


        # Estimate mu, std using gaussian fit
        for col in params_df.columns:
            series = params_df[col]
            mu,std = norm.fit(series)   
            params[col] = {"best":series.iloc[0],"min":series.quantile(0.025),"max":series.quantile(0.975),"mu_norm":mu,"std_norm":std,"min_norm":mu-std/2,"max_norm":mu+std/2}

        if summary:
            return pd.DataFrame(params).T
        else:
            return params



    def sample_params(self,n = 1000,q = 0.05,norm_fit = False):



        if norm_fit:
            # Estimate parameters distribution
            params = self.estimate_params_distributions(q = q)
            
            # Sample using normal distributions
            params = {k:norm.rvs(v["mu_norm"],v["std_norm"],size = n) for k,v in params.items() if k!="value"}

            # Unzip params
            keys = list(params.keys())
            values = list(zip(*params.values()))
            params = [{keys[i]:values[j][i] for i in range(len(keys))} for j in range(len(values))]
        
        else:
            params = (
                self.estimate_params_distributions(q = q,return_df = True)
                .drop(columns = ["value"])
                .to_dict(orient = "records")
            )

        return params
