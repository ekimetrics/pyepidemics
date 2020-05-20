"""
Base function to download, fetch and load datasets
"""

import logging
import os
import requests

def get_data_home(data_home=None):
    if data_home is None:
        data_home = os.path.dirname(os.path.realpath(__file__))
    data_home = os.path.join(data_home, 'data')
    if not os.path.exists(data_home):
        os.makedirs(data_home)
    return data_home

def download_file(url, filepath):
    logging.info(f"Downloading file from {url} to {filepath}.")
    response = requests.get(url)
    with open(filepath, 'wb') as f:
        f.write(response.content)