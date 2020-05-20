

# Quickstart
## Creating a SIR model

```python
# Import library
from pyepidemics.models import SIR

# Let's take approximate parameters during COVID19 epidemics
N = 67e6
beta = 3.3/4
gamma = 1/4

# Instantiate model with epidemiological parameters
sir = SIR(N,beta,gamma)

# Solve for one infected case for 100 days starting from 2020-01-24
states = sir.solve(1,n_days = 100,start_date = "2020-01-24")

# Visualize epidemic curves using matplotlib (plotly available)
states.show(plotly = False)
```

## Creating a custom compartmental model
Here is the example to create a model like the SIR described above

```python
from pyepidemics.models import CompartmentalModel


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

```