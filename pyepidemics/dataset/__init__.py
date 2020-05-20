"""
The :mod:`covid.datasets` module includes utilities to load datasets:
  - daily cases (confirmed, deaths ) per departments
  - number of ICU bed available by hospitals and regional centers
"""

from ._base import get_data_home
from ._base import download_file
from ._fetch import fetch_daily_case
from ._fetch import fetch_population
from ._fetch import fetch_contact_matrix
from ._fetch import fetch_daily_case_france
from ._fetch import fetch_daily_case_departement
from ._fetch import fetch_list_available_departements
from ._build import get_contact_matrices
from ._fetch_geojson import fetch_geojson
from ._fetch_bed import fetch_bed, fetch_bed_rea
from ._fetch import fetch_production_economics
