# Welcome to pyepidemics documentation
![logo](img/logo_pyepidemics.png)

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



!!! warning
    **This library is under active development, please contact [Théo Alves Da Costa](mailto:theo.alvesdacosta@ekimetrics.com) if you need more information and would like to contribute**



# Contributors
![](img/ekimetrics.png)

The library has been initially developed by [Ekimetrics](www.ekimetrics.com) under the coalition of French AI companies CoData or help French government response to the COVID19 pandemics. Main contributors are:

- [Théo Alves Da Costa](mailto:theo.alvesdacosta@ekimetrics.com), Ekimetrics
- Léo Grosjean, Ekimetrics
- Pierre Carles, Ekimetrics
- Nicolas Chesneau, Ekimetrics
- Marianne Chehade, Ekimetrics
- Jean-Baptiste Remy

