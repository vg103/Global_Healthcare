import unittest
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go


def import_data(data_path):
    df = pd.read_csv(data_path, header=0, encoding = "utf-8", na_values=["NA", "null", "", "NaN"])

    df = df.dropna(axis = 1, thresh=1)

    return df

def pivot_IHME(df):

    pivoted_df = df.pivot_table(index=['location', 'sex', 'cause', 'year'], 
                            columns='measure', 
                            values='val', 
                            aggfunc='first') 

    # Reset the index if needed
    pivoted_df = pivoted_df.reset_index()

    # Rename the columns for clarity
    pivoted_df = pivoted_df.rename(columns={'death': 'death_rate', 'incidence': 'incidence_rate'})

    #pivoted_df.to_csv('/home/nmina/Global_Healthcare/data/pivotted_dataframe_IHME.csv', index=False)
       
    return pivoted_df

def pivot_WHO(df):

    pivoted_df = df.pivot_table(index=['ParentLocation', 'Location', 'Period'], 
                            columns='Indicator', 
                            values='Value', 
                            aggfunc='first') 

    # Reset the index if needed
    pivoted_df = pivoted_df.reset_index()
    pivoted_df = pivoted_df.drop('ParentLocation',axis='columns')
    #pivoted_df.to_csv('/home/nmina/Global_Healthcare/data/pivotted_dataframe_WHO.csv', index=False)
       
    return pivoted_df

def graph_docs_by_country(df):

    # filter to the year 2023
    df_2023 = df[df['Period'] == 2023]    
    
    fig = px.bar(df_2023, x = 'Location', y = 'Medical doctors (per 10,000)', title = "Medical Doctors per 10,000 people in the Population in 2023", labels = {'Location' : 'Country'})
    
    fig.write_image("doctors_per_10000_2023.png")
    
    return

def drop_sex(df):
    #using inplace=TRUE turned df into type None - confirm with group
    df = df.drop(df[df.sex=="Male"].index, axis="index")
    df = df.drop(df[df.sex=="Female"].index, axis="index")
    df = df.drop('sex', axis="columns")
    return df

def ag_over_cause(df):
    df = df.groupby(['location','year'],as_index=False).sum()
    df = df.drop('cause',axis='columns')
    return df

def make_medical_data_df(med_df, nurse_df, pharm_df, dent_df):
    
    keep_columns = ['Location', 'Period', 'Value']
    
    med_df = med_df[keep_columns]
    nurse_df = nurse_df[keep_columns]
    pharm_df = pharm_df[keep_columns]
    dent_df = dent_df[keep_columns]

    med_df = med_df.rename(columns={'Value': 'Medical Doctors per 10,000'})
    nurse_df = nurse_df.rename(columns={'Value': 'Nurses and Midwifes per 10,000'})
    pharm_df = pharm_df.rename(columns={'Value': 'Pharmacists per 10,000'})
    dent_df = dent_df.rename(columns={'Value': 'Dentists per 10,000'})

    import pandas as pd

    # Inner merging four DataFrames on 'Location' and 'Period'
    merged_df = med_df.merge(nurse_df, on=['Location', 'Period'], how='inner') \
               .merge(pharm_df, on=['Location', 'Period'], how='inner') \
               .merge(dent_df, on=['Location', 'Period'], how='inner')

    return merged_df

def main():

    print(f"Current Directory: {os.getcwd()}")# Check your current working directory

    # Check if files is found
    #file_path = "/home/nmina/Global_Healthcare/data/"
    file_path = '/home/gdiaz21/Global_Healthcare/data/'
    #if os.path.exists(file_path):
        #print(f"File found: {file_path}")
    #else:
        #print(f"File NOT found: {file_path}")

    # makes medical data dataframe (with all provider indicators)
    med_docs = import_data(file_path + r'medical-doctors.csv')
    nurse_midwifes = import_data(file_path + r'nursery-midwifery.csv')
    pharms = import_data(file_path + r'pharmacists.csv')
    dentists = import_data(file_path + r'dentistry.csv')
    new_data_WHO = make_medical_data_df(med_docs, nurse_midwifes, pharms, dentists)
    new_data_WHO.to_csv('/home/gdiaz21/Global_Healthcare/data/new_data_who.csv')
    print(new_data_WHO.info())

    # read in WHO dataset
    # THE FUNCTIONALITY OF THIS CODE DEPENDS ON CURRENT WORKING DIRECTORY
        # ex: my current working directory when running this is /home/gdiaz21/Global_Healthcare/
    data_WHO = import_data(file_path + "WHO data.csv") # this path will not work for everyone
    data_WHO = data_WHO.drop(['ParentLocationCode', 'SpatialDimValueCode', 'IndicatorCode', 'Period type', 'Location type', 'ValueType', 'FactComments', 'FactValueNumeric', 'Language', 'IsLatestYear', 'DateModified'], axis=1)

    #print(data_WHO.info())

    # read in Institute for Health Metrics and Evaluation
    data_IHME_1 = import_data(file_path + "IHME-1.csv")
    data_IHME_2 = import_data(file_path + "IHME-2.csv")
    data_IHME_combined = pd.concat([data_IHME_1, data_IHME_2], axis=0, ignore_index=True)
    data_IHME_combined = data_IHME_combined.drop(['age', 'metric', 'upper', 'lower'], axis=1)

    #print(data_IHME_combined.info())

    df_IHME = pivot_IHME(data_IHME_combined)
    df_WHO = pivot_WHO(data_WHO)
    df_IHME = drop_sex(df_IHME)
    df_IHME = ag_over_cause(df_IHME)
    both_sources = pd.merge(df_IHME, df_WHO, how="inner", left_on=['location','year'],right_on=['Location','Period'])
    both_sources.info()
    both_sources.info
    #both_sources = both_sources.drop('Location',axis='columns')
    #both_sources = both_sources.drop('Period',axis='columns')
    
    #graph_docs_by_country(df_WHO)

    both_sources.to_csv('inner_merged_data.csv',index=False)

    return

if __name__ == '__main__':
    main()