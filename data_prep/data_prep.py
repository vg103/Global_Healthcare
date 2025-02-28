"""
This module contains functions for data preparation.
"""

import pandas as pd


def import_data(data_path=""):
    """
    Import data from a CSV file.

    Parameters:
    data_path (str): The path to the CSV file.

    Returns:
    DataFrame: A pandas DataFrame containing the imported data.
    """
    df = pd.read_csv(data_path)
    return df
