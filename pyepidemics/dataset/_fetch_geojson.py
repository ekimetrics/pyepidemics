import logging
from os.path import join, exists

from . import get_data_home
from . import download_file
from ..utils import load_json

URL = "https://france-geojson.gregoiredavid.fr/repo/{}.geojson"

level_name_dict = {'DPT': 'departements', 'REG': 'regions'}

def fetch_geojson(data_home=None, level='dpt', return_data=False):
    """
    Download a feature collection of geojson for each department in France
    Return the geojson dataset.
    Arguments:
    ---------
      - level['dpt' or 'reg']: if you want departmental geojson ('dpt') or regional ('reg')
      - return_data [bool]: return raw data or not
    Example:
    -------
      $ from covid.dataset import fetch_geojson
      $ departements = fetch_geojson(level='dpt', return_data=True)
    """
    data_home = get_data_home(data_home=data_home)
    assert level.upper() in ['DPT', 'REG']
    level_name = level_name_dict[level.upper()]
    
    filepath = join(data_home, f"{level_name}.geojson")
    if exists(filepath):
            logging.info(f"File already exists at {filepath}")
    else:
            download_file(URL.format(level_name), filepath)
    
    if return_data:
        data = load_json(filepath)
        return data