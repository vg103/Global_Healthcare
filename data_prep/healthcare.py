"""
Code to read in, clean, and merge data from the 
    Institute for Health Metrics and Evaluation (IHME) and the World Health Organization (WHO).
"""
import os

import pandas as pd

def import_data(data_path):
    """Reads in data from the specified path and returns a dataframe of the data
    Args: path to the data file
    Returns: pandas DataFrame"""
    df = pd.read_csv(data_path, header=0, encoding = "utf-8", na_values=["NA", "null", "", "NaN"])
    df = df.dropna(axis = 1, thresh=1)
    return df

def pivot_ihme(df):
    """Pivots the IHME data to have one row per location
    Args: pandas DataFrame, should only be called on the IHME df
    Returns: the updated pandas DataFrame"""
    pivoted_df = df.pivot_table(index=['location', 'sex', 'cause', 'year'],
                            columns='measure',
                            values='val',
                            aggfunc='first')
    # Reset the index if needed
    pivoted_df = pivoted_df.reset_index()
    # Rename the columns for clarity
    pivoted_df = pivoted_df.rename(columns={'death': 'death_rate', 'incidence': 'incidence_rate'})
    pivoted_df.to_csv('final_data/final_IHME.csv',index=False)
    return pivoted_df

def drop_sex(df):
    """removes all rows with data specific to one sex and the column labeling sex group of data
    Args: pandas DataFrame, should only be called on IHME
    Returns: the updated df"""
    #using inplace=TRUE turned df into type None - confirm with group
    df = df.drop(df[df.sex=="Male"].index, axis="index")
    df = df.drop(df[df.sex=="Female"].index, axis="index")
    df = df.drop('sex', axis="columns")
    return df

def ag_over_cause(df):
    """aggregates the input dataframe over the various causes of death
    Args: pandas DataFrame, should only be called on IHME
    Returns: pandas DataFrame with just one row per country per year"""
    df = df.groupby(['location','year'],as_index=False).sum()
    df = df.drop('cause',axis='columns')
    return df

def make_medical_data_df(med_df, nurse_df, pharm_df, dent_df):
    """Merges the four medical provider DataFrames into one DataFrame
    Args: four pandas DataFrames for each of the medical provider categories from WHO
    Returns: one pandas DataFrame with all information"""
    keep_columns = ['Location', 'Period', 'Value']

    med_df = med_df[keep_columns]
    nurse_df = nurse_df[keep_columns]
    pharm_df = pharm_df[keep_columns]
    dent_df = dent_df[keep_columns]

    med_df = med_df.rename(columns={'Value': 'Medical Doctors per 10,000'})
    nurse_df = nurse_df.rename(columns={'Value': 'Nurses and Midwifes per 10,000'})
    pharm_df = pharm_df.rename(columns={'Value': 'Pharmacists per 10,000'})
    dent_df = dent_df.rename(columns={'Value': 'Dentists per 10,000'})

    # Inner merging four DataFrames on 'Location' and 'Period'
    merged_df = med_df.merge(nurse_df, on=['Location', 'Period'], how='inner') \
               .merge(pharm_df, on=['Location', 'Period'], how='inner') \
               .merge(dent_df, on=['Location', 'Period'], how='inner')

    return merged_df

def process_healthcare_data(file_path):
    """function that processes all data using the functions in this file"""

    # Check if files is found
    if os.path.exists(file_path):
        print(f"File found: {file_path}")
    else:
        print(f"File NOT found: {file_path}")

    # makes medical data dataframe (with all provider indicators)
    med_docs = import_data(file_path + r'medical-doctors.csv')
    nurse_midwifes = import_data(file_path + r'nursery-midwifery.csv')
    pharms = import_data(file_path + r'pharmacists.csv')
    dentists = import_data(file_path + r'dentistry.csv')

    new_data_who = make_medical_data_df(med_docs, nurse_midwifes, pharms, dentists)
    new_data_who.to_csv('final_data/final_who.csv')

    # read in Institute for Health Metrics and Evaluation
    data_ihme_1 = import_data(file_path + "IHME-1.csv")
    data_ihme_2 = import_data(file_path + "IHME-2.csv")
    data_ihme_combined = pd.concat([data_ihme_1, data_ihme_2], axis=0, ignore_index=True)
    data_ihme_combined = data_ihme_combined.drop(['age', 'metric', 'upper', 'lower'], axis=1)

    df_ihme = pivot_ihme(data_ihme_combined)
    df_ihme = drop_sex(df_ihme)
    df_ihme = ag_over_cause(df_ihme)
    both_sources = pd.merge(df_ihme, new_data_who, how="inner",
        left_on=['location','year'],right_on=['Location','Period'])
    both_sources.info()
    both_sources = both_sources.drop('Location',axis='columns')
    both_sources = both_sources.drop('Period',axis='columns')

    both_sources.to_csv('final_data/inner_merged_data.csv',index=False)

def main():
    """Main function to run the code"""
    print(f"Current Directory: {os.getcwd()}")# Check your current working directory

    file_path = "../data/"
    process_healthcare_data(file_path)


if __name__ == '__main__':
    main()
