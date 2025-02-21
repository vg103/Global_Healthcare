import pandas as pd

def import_data(data_path=""):
    df = pd.read_csv(data_path)

    return df