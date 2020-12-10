"""
Two types of datasets available:
  - daily_cases (departments)
  - population (departments, regions)

ToDo:
  - Number of bed available by region/departments
  - split _fetch for each type of sources ?
"""

import logging
from os.path import join, exists

import pandas as pd

from . import get_data_home
from . import download_file
from ..utils import clean_series

CASE_URL = "https://raw.githubusercontent.com/opencovid19-fr/data/master/"\
    "dist/chiffres-cles.csv"

POP_URL = {
    "DPT": "https://www.insee.fr/fr/statistiques/fichier/1893198/"\
       "estim-pop-dep-sexe-gca-1975-2020.xls",
    "REG": "https://www.insee.fr/fr/statistiques/fichier/1893198/"\
            "estim-pop-nreg-sexe-gca-1975-2020.xls"
}

BED_URL = "https://drees.solidarites-sante.gouv.fr/IMG/xlsx/"\
    "drees_lits_reanimation_2013-2018.xlsx"

CONTACT_URL = "https://ndownloader.figshare.com/files/2157552"

def fetch_contact_matrix(data_home=None, force_download=False, update=False, return_data=False):
    """
    Downloads the raw_data from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133203
    Then builds the contact matrices required based on this raw data.
    Arguments:
    ---------
      - data_home: where to save file (default in covid.dataset.data)
      - force_download: if raw data already exists it is downloaded again only if force_download is true.
      - update [bool]: if final file already exists, update with more udpated data or use existing file
      - return_data [bool]: return dataframe or not
    Example:
    -------
      $ from covid.dataset import fetch_contact_matrix
      $ data = fetch_contact_matrix(return_data=True)
    """
    data_home = get_data_home(data_home=data_home)

    raw_filepath = join(data_home, "raw_contact_matrix.xlsx")
    if not exists(raw_filepath) or force_download:
        download_file(CONTACT_URL, raw_filepath)

    else:
        logging.info(f"Raw file already exists at {raw_filepath}")

    filepath = join(data_home, "contact_matrix.xlsx")
    if not exists(filepath) or update:
        raw_data = pd.read_excel(raw_filepath, skiprows=[0,1,2], header=None)
        data = _process_contact(raw_data)
        data.to_csv(filepath, index=False, sep=',')

    else:
        data = pd.read_csv(filepath, sep=',')

    if return_data:
        return data

def _process_contact(raw_data, age_groups_boundaries=[18,65]):
    """
    Builds the contact matrices based on the raw_data

    Arguments:
    ---------
      - data (pd.DateFrame): raw_data
      - age_groups_bondaries: [18, 65] => [0,18], ]18,65[, [65,)
    """
    def parse_one_line(line):
        """
        Transforms one line of the data set into one dataset of contacts.
        """
        if line[1184] == 0:
            return pd.DataFrame()

        data_frames = []
        departement, age1, sex1 = line[27], line[4], line[6]
        for day_index in [54, 619]:
            week_day, vacation = line[day_index+2], line[day_index+3]
            contact = 0
            contact_index = day_index + 5 + contact * 14
            while contact<40 and not sum(line[contact_index+4: contact_index+11])==0\
                and not pd.isnull(line[contact_index+2]):
                df = pd.DataFrame({"ID": line[1],
                                   "departement": departement,
                                   "week_day": week_day, "vacation": vacation, 
                                   "age1": age1, "sex1": sex1,
                                   "age2": line[contact_index+2], 
                                   "sex2": line[contact_index+3],
                                   "domicile": line[contact_index+4],
                                   "ecoles": line[contact_index+5],
                                   "travailClos": line[contact_index+6],
                                   "chezProchesLieuxClos": line[contact_index+7],
                                   "autresLieuxClos(resto..)": line[contact_index+8],
                                   "transport": line[contact_index+9],
                                   "ouvert": line[contact_index+10],
                                   "duration": line[contact_index+13]},
                                  index=[0])

                data_frames.append(df)
                contact+=1
                contact_index = day_index + 5 + contact * 14

        if len(data_frames) > 0:
            to_return = pd.concat(data_frames)

        else: 
            return pd.DataFrame()

        return to_return

    data = pd.concat([parse_one_line(raw_data.loc[i,:]) for i in range(raw_data.shape[0])])
    data = data.dropna(axis=0).astype(int)

    data.departement = data.departement.astype("object")
    data.week_day = data.week_day.astype("object")
    data.vacation = data.vacation.replace({1: "oui", 2: "non"})
    data.sex1 = data.sex1.replace({1: "homme", 2: "femme"})
    data.sex2 = data.sex2.replace({1: "homme", 2: "femme"})
    data.duration = data.duration.replace({1: "<5", 2: "5-15", 3: "15-1h",
                                          4: "1h-4h", 5: ">4h"})

    return data

def fetch_daily_case(data_home=None, update=True, return_data=False,download = False):
    """
    Download daily case in France per departement
    Can return dataframe or not
    Arguments:
    ---------
      - data_home: where to save file (default in covid.dataset.data)
      - update [bool]: if already exists, update with more udpated data or use existing file
      - return_data [bool]: return dataframe or not
    Example:
    -------
      $ from covid.dataset import fetch_daily_case
      $ data = fetch_daily_case(return_data=True)
    """

    if download:

        data_home = get_data_home(data_home=data_home)
        
        filepath = join(data_home, "daily_cases.csv")
        if exists(filepath):
            if update:
                download_file(CASE_URL, filepath)
            else:
                logging.info(f"File already exists at {filepath} and update = False")
        else:
                download_file(CASE_URL, filepath)
        
        if return_data:
            data = pd.read_csv(filepath)
            return data

    else:
        data = pd.read_csv(CASE_URL)
        return data



def fetch_daily_case_france(return_data = True,smooth = True):

    # Get cases from utils function
    cases = (
        fetch_daily_case(return_data = True)
        .query("granularite =='pays'")
        .query("source_nom=='Ministère des Solidarités et de la Santé'")
        [["date","cas_confirmes","deces","gueris","hospitalises","reanimation"]]
        .drop_duplicates(subset = ["date"])
        .fillna(0.0)
        .iloc[:-1] # Safety check
        .assign(date = lambda x : pd.to_datetime(x["date"],errors="coerce"))
        .dropna(subset = ["date"])
        .set_index("date")
    )

    # Reindex and interpolate
    start,end = cases.index[0],cases.index[-1]
    date_range = pd.date_range(start,end,freq="D")
    cases = cases.reindex(date_range).interpolate()

    # Clean and logsmooth
    cases["I"] = clean_series(cases["cas_confirmes"],logsmooth = smooth)
    cases["Is"] = clean_series(cases["cas_confirmes"] - (cases["deces"] + cases["gueris"]),logsmooth=smooth)
    cases["D"] = clean_series(cases["deces"],logsmooth = smooth)
    cases["R"] = clean_series(cases["gueris"],logsmooth = smooth)
    cases["H"] = clean_series(cases["hospitalises"],logsmooth = smooth)
    cases["ICU"] = clean_series(cases["reanimation"],logsmooth = smooth)

    return cases


def fetch_list_available_departements(without_prefix = True):
    dep =  list(
        fetch_daily_case(return_data = True)
        .query(f"granularite=='departement'")
        ["maille_code"]
        .unique()
    )
    if without_prefix:
        dep = [x.replace("DEP-","") for x in dep]
    return dep
        



def fetch_daily_case_departement(dep,return_data = True,smooth = True):

    # Get cases from utils function
    cases = (fetch_daily_case(return_data = True)
        .query(f"granularite=='departement' and maille_code=='DEP-{dep}'")
        .query("source_nom=='Santé publique France Data'")
        [["date","deces","gueris","hospitalises","reanimation"]]
        .drop_duplicates(subset = ["date"])
        .fillna(0.0)
        .assign(date = lambda x : pd.to_datetime(x["date"]))
        .set_index("date")
    )

    # Reindex and interpolate
    start,end = cases.index[0],cases.index[-1]
    date_range = pd.date_range(start,end,freq="D")
    cases = cases.reindex(date_range).interpolate()

    # Clean and logsmooth
    cases["D"] = clean_series(cases["deces"],logsmooth = smooth)
    cases["R"] = clean_series(cases["gueris"],logsmooth = smooth)
    cases["H"] = clean_series(cases["hospitalises"],logsmooth = smooth)
    cases["ICU"] = clean_series(cases["reanimation"],logsmooth = smooth)

    return cases


def fetch_population(data_home=None, return_data=False, level='dpt', year=2020):
    """
    Download population by [Region / Department] for a given year in data_home.
    Can return dataframe or not
    Example:
    -------
      $ from covid.dataset import fetch_population
      $ pop_dpt_2020 = fetch_population(level='dpt', year=2020, return_data=True)
    """
    assert level.upper() in ['DPT', 'REG'], "The granularity level is limited to Departments ('dpt') or Regions ('reg')"
    
    data_home = get_data_home(data_home=data_home)

    filepath = join(data_home, f"pop_{level.lower()}_{str(year)}.csv")
    if not exists(filepath):
        data = pd.read_excel(POP_URL[level.upper()], sheet_name=str(year), header=3)
        data = _format_pop(data)
        data.to_csv(filepath, index=False, sep=',')
    else:
        logging.info(f"File already exists at {filepath}")
        data = pd.read_csv(filepath)
    
    if return_data:
        return data

def _format_pop(data):
    
    # Rename columns
    col_0 = list(data.columns)
    for i, col in enumerate(col_0):
        if 'unnamed' in col.lower():
            col_0[i] = col_0[i-1]
    col_1 = list(data.iloc[0].values)
    col_1 = [
        col.replace('à', '_').replace('ans', '').replace(' ', '').replace('etplus', '+') 
        if col==col
        else ''
        for col in col_1]
    
    data_ = data.iloc[1:].copy() # drop first line
    data_.columns = [f"{c1}_{c2}" for c1, c2 in zip(col_0, col_1)] #join columns

    if 'Départements_' in data_.columns:
        data_.columns = [f"{col}ID" if i==0 else col for i, col in enumerate(data_.columns)]

    data_ = data_.dropna()

    return data_

def fetch_bed(data_home=None, return_data=False):
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
    if not exists(filepath):
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


def fetch_production_economics(data_home=None):
    """
    Download daily case in France per departement
    Can return dataframe or not
    Arguments:
    ---------
      - data_home: where to save file (default in covid.dataset.data)
      - update [bool]: if already exists, update with more udpated data or use existing file
      - return_data [bool]: return dataframe or not
    Example:
    -------
      $ from covid.dataset import fetch_daily_case
      $ data = fetch_daily_case(return_data=True)
    """
    data_home = get_data_home(data_home=data_home)
    
    filepath = join(data_home, "economics_data.xlsx")
    
    df = pd.read_excel(filepath)
    df_dept = pd.read_excel(filepath, sheet_name ="data_departement")

    return df, df_dept