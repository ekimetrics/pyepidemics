import logging
from os.path import join, exists

import pandas as pd

from . import get_data_home
from . import download_file

BED_URL = "https://drees.solidarites-sante.gouv.fr/IMG/xlsx/"\
    "drees_lits_reanimation_2013-2018.xlsx"

def fetch_bed(data_home=None, update=False, return_data=False):
    """
    Download beds by departements for 2018
    Can return dataframe or not
    Example:
    -------
      $ from covid.dataset import fetch_bed
      $ pop_dpt_2020 = fetch_bed(return_data=True)

    File documentation:
    -------------------
      - SSA : service de santé des armées
      - USIC : unité de soins intensifs de cardiologie
      - UNV : unité neuro-vasculaire.
    """
    data_home=get_data_home(data_home=data_home)
    filepath = join(data_home, "beds_dpt.csv")
    if not exists(filepath) or update:
        download_file(BED_URL, filepath)
        data = pd.read_excel(filepath, sheet_name='Détails_statut_type_2018', header=9)
        data = _format_bed(data)
        data.to_csv(filepath, index=False, sep=',')
    else:
        logging.info(f"File already exists at {filepath}.")
        data = pd.read_csv(filepath)
    if return_data:
        return data

def _format_bed(data):
    rename_dict = {
        "Public": "rea_adultes_public",
        "Privé BNL": "rea_adultes_bnl",
        "Privé BL": "rea_adultes_bl",
        "Public.1": "rea_enfants_public",
        "Privé BNL.1": "rea_enfants_bnl",
        "Privé BL.1": "rea_enfants_bl",
        "Public.2": "intensif_usic_public",
        "Privé BNL.2": "intensif_usic_bnl",
        "Privé BL.2": "intensif_usic_bl",
        "Public.3": "intensif_unv_public",
        "Privé BNL.3": "intensif_unv_bnl",
        "Privé BL.3": "intensif_unv_bl",
        "Public.4": "intensif_autres_public",
        "Privé BNL.4": "intensif_autres_bnl",
        "Privé BL.4": "intensif_autres_bl",
        "Public.5": "continu_adultes_public",
        "Privé BNL.5": "continu_adultes_bnl",
        "Privé BL.5": "continu_adultes_bl",
        "Public.6": "continu_enfants_public",
        "Privé BNL.6": "continu_enfants_bnl",
        "Privé BL.6": "continu_enfants_bl"
    }
    data_ = data.rename(columns=rename_dict)
    return data_


def fetch_bed_rea(update=False, simplify=True, return_dict=True):
    """
    Import number of reanimation beds per departments (metropol)
    The 96 metropolitan departments are returned
    Parameters:
    -----------
      - update[bool]: if the raw dataset of beds is already downloaded, rewrite it or not locally
      - simplify[bool]: if you only want the number of beds for adult, children and total or the total dataset
      - return_dict[bool]: if you want to get data in a dictionnary format or in a pandas DataFrame
    Example:
    --------
      $ from covid.dateset import fetch_bed_rea
      $ bed_rea = fetch_bed_rea(simplify=True)
    """
    beds = (
        fetch_bed(update=update, return_data=True)
        .set_index('Code')
        .pipe(lambda x: x.filter([c for c in x.columns if 'rea' in c]))
        .pipe(lambda x: x.assign(rea_total=lambda y: y.sum(axis=1)))
        .pipe(lambda x: x.assign(
            rea_enfants=lambda y: y.filter([c for c in y.columns if 'enfant' in c]).sum(axis=1))
             )
        .pipe(lambda x: x.assign(
            rea_adultes=lambda y: y.filter([c for c in y.columns if 'adulte' in c]).sum(axis=1))
             )
        .pipe(lambda x: x.filter(['rea_total', 'rea_enfants', 'rea_adultes']) if simplify else x)
        .drop(['FR', 'MET', '971', '972', '973', '974', '976'], axis=0)
    )
    if return_dict:
        return beds.to_dict(orient='index')
    else:
        return beds
