
# Experimental

import neptune
import json

API_KEY = "xxx" # replace by API_KEY
neptune.init('theoalves/sandbox',api_token = API_KEY)

def neptune_callback(study,trial):
    neptune.create_experiment(name='minimal_example',params = trial.params)
    neptune.log_metric("loss",trial.value)