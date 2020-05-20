import pandas as pd
import matplotlib.pyplot as plt

from hyperopt import hp
from hyperopt import fmin, tpe, Trials


class HyperoptParamsOptimizer:
    def __init__(self,model):
        """Hyperopt is a little faster than optuna but has much less other capabilities
        By default the Optuna Optimizer will be taken in optimizer.py script
        """

        # Store model as attribute
        self.model = model
    

    @staticmethod
    def _infer_hp_space(key,value):
        if isinstance(value,tuple) and len(value) == 2:
            return hp.uniform(key,value[0],value[1])
        elif isinstance(value,dict):
            return hp.normal(key,value["mu"],value["sigma"]),
        else:
            return Exception(f"Space {key} for optimization is not recognized {value}, should be tuple or dict")


    def _make_space(self,space):
        new_space = {}
        for key,value in space.items():
            new_space[key] = self._infer_hp_space(key,value)
        return new_space


    def run(self,true,space,init_state,objective_fn = None,n = 100):

        # Convert to hyperopt search space
        space = self._make_space(space)

        # Prepare objective function
        if objective_fn is None:
            objective_fn = lambda params : self.model.objective(true,params,init_state)

        # Trials object to record each optimization
        self.trials = Trials()


        # Find best paramaters
        print(f"[INFO] Launching parameters optimization\n")
        best = fmin(
            fn=objective_fn,
            space=space,
            trials=self.trials,
            algo=tpe.suggest,
            max_evals=n
        )

        print(f"\n... Found best solution {best}")
        return best

