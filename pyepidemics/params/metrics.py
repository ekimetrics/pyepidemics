
import numpy as np
from sklearn.metrics import mean_squared_error



def custom_loss(pred,true,cols = None,normalize = True):

    # Get default columns if not given
    if cols is None:
        cols = true.columns.tolist()

    # Helper function computing MSE
    def error(y_pred, y_true,normalize = True):
        if normalize:
            return mean_squared_error(y_pred, y_true)/(np.max(y_true)**2)
        else:
            return mean_squared_error(y_pred,y_true)

    # Iterate over each column of interest to compute loss
    loss = 0
    loss_dict = {}
    for col in cols:
        loss_col = error(pred[col],true[col],normalize = normalize)
        loss_dict[f"loss_{col}"] = loss_col
        loss += error(pred[col],true[col],normalize = normalize)

    # Normalize to get RMSE
    loss = np.sqrt(loss)
    loss_dict["loss"] = loss

    # Convert to float over numpy float to ensure serialization
    loss_dict = {k:float(v) for k,v in loss_dict.items()}

    return loss,loss_dict

