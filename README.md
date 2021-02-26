# pyepidemics
![logo](docs/img/logo_pyepidemics.png)

**Open-source epidemics modeling Python library**

*pyepidemics* is a Python library to easily manipulate epidemiological models (SIR, SEIR, COVID19), forecast, and test policy scenarios. Main features are: 
- Creation of classical compartmental models (SIR, SEIR, SEIDR, etc...)
- Creation of COVID19 related model (with ICU and different levels of symptoms)
- Creation of custom compartmental model
- Easy extend to compartmental model on different levels (by age, by region, by age and region, etc...)
- Implementation of contact matrices
- Implementation of policies (lockdown, tracing, testing, etc...)
- Calibration of epidemiological parameters on real-world data using Bayesian optimization 
- Data helpers to get up-to-date data (cases, beds availability, population contact matrices) (NB as of today only for France cases)
- Simple curve fitting algorithms
- Economics modeling on consumption and production

> **This library is under active development, please contact [Théo Alves Da Costa](mailto:theo.alvesdacosta@ekimetrics.com) if you need more information and would like to contribute**



# Contributors
![](docs/img/ekimetrics.png)

The library has been initially developed by [Ekimetrics](www.ekimetrics.com) under the coalition of French AI companies CoData ot help French government response to the COVID19 pandemics. Main contributors are:
- [Théo Alves Da Costa](mailto:theo.alvesdacosta@ekimetrics.com), Ekimetrics
- Emilie Rannou, Ekimetrics
- Léo Grosjean, Ekimetrics
- Pierre Carles, Ekimetrics
- Nicolas Chesneau, Ekimetrics
- Marianne Chehade, Ekimetrics
- Jean-Baptiste Remy

# Installation

## Install using pip
We recommend to create a virtual environment first, then you can install the library using the command 
```
pip install pyepidemics
```
The repo is on PyPI at https://pypi.org/project/pyepidemics/

## Install from source
You can also install the repository by cloning it locally and using it either locally or installing the wheel by calling first
```
python setup.py sdist bdist_wheel
```


# Documentation
Documentation is available at https://ekimetrics.github.io/pyepidemics

## Folder structure
```
- pyepidemics/          --------- Python library centralizing source code
    - dataset/          --------- Helpers to get up-to-date COVID19 datasets
    - models/           --------- Compartmental models code
    - params/           --------- Epidemiological parameters calibration optimizers
    - policies/         --------- Scenarios implementation
    - visualization/    --------- Visualization helpers (chloropleth maps using pydeck)
- data/                 --------- Local datasets if needed
- docs/                 --------- Documentation and tutorial notebooks
- notebook/             --------- Development notebooks
- references/           --------- Reports and research papers
- scripts/              --------- Automation scripts on calibration
- requirements.txt      --------- Python requirements 
```


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

# Contribution guidelines
> WIP

# References
- https://towardsdatascience.com/infectious-disease-modelling-beyond-the-basic-sir-model-216369c584c4



# License
MIT License
