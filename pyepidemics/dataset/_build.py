
# Base Data Science snippet
import pandas as pd
import numpy as np
import json
import pickle
from os.path import join, exists

from . import fetch_contact_matrix
from . import get_data_home

def get_contact_matrices(data_home=None, age_boundaries=[18, 65], update=False,
                        return_matrices=True):


    data_home = get_data_home(data_home=data_home)
    filepath = join(data_home, "contact_matrices.json")

    if not exists(filepath) or update:
        data = fetch_contact_matrix(return_data=True)

        data.duration.replace({"<5": 0.08, "5-15": 0.25, "15-1h": 0.75, "1h-4h": 3, ">4h": 4}, inplace=True)
        for column in ["domicile", "ecoles", "travailClos", "chezProchesLieuxClos",
                   "autresLieuxClos(resto..)", "transport"]:
            data[column] = data[column] * data["duration"]

        data["ouvert"] = data["ouvert"] * data["duration"] * 0.2

        vacations = ["oui", "non"]
        places = ["domicile", "ecoles", "travailClos", "chezProchesLieuxClos", "autresLieuxClos(resto..)", "transport", "ouvert"]

        age_boundaries.append(np.infty)
        age_boundaries.insert(0, -1)
        age_groups = [[x,y] for x,y in zip(age_boundaries[:-1], age_boundaries[1:])]

        contact_matrices = {vacation: {place: [] for place in places} for vacation in vacations}
        for vacation in vacations:
            time_select = (data.vacation == vacation)
            data_temp = data[time_select]
            for Id in data_temp.ID.unique():
                ind = data_temp["ID"] == Id
                age1 =  data_temp.loc[ind,"age1"].mean()
                i = np.where([group[0] < age1 and age1 <= group[1] for group in age_groups])[0].item()
                for place in places:
                    matrice = np.zeros((len(age_groups),len(age_groups)))
                    for j in range(len(age_groups)):
                        age_group2 = ((age_groups[j][0] < data_temp.age2) & (data_temp.age2 < age_groups[j][1]))
                        matrice[i,j] = data_temp.loc[ind & age_group2, place].sum() 

                    contact_matrices[vacation][place].append(matrice)

            contact_matrices[vacation] = {k:np.mean(v, axis=0).tolist() for k,v in contact_matrices[vacation].items()}

        with open(filepath, "w") as f:
            json.dump(contact_matrices, f)
            f.close()

    if return_matrices:
        with open(filepath, "r") as f:
            matrices = json.load(f)
            f.close()

        for vacations in ["oui", "non"]:
            for key in matrices[vacations].keys():
                matrices[vacations][key] = np.array(matrices[vacations][key])

        return matrices

if __name__=="__main__":
    get_contact_matrices()







