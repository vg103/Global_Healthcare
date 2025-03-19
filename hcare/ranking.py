"""
Script to run the ranking algorithm on the inner merged data
Returns a pandas dataframe with the composite score and rank for each country in each year
"""
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

def normalize_data(df, indicator_cols, group_by='year'):
    """
    Normalize indicator columns within each year group using MinMax scaling.
    Returns a DataFrame with normalized indicator values.
    """
    normalized_df = pd.DataFrame()
    scaler = MinMaxScaler()
    # removed group as a second iterator through df.groupby(group_by)
    for _,sub_df in df.groupby(group_by):
        sub_df = sub_df.copy()
        sub_df[indicator_cols] = scaler.fit_transform(sub_df[indicator_cols])
        normalized_df = pd.concat([normalized_df, sub_df], ignore_index=True)
    return normalized_df


def adjust_negative_indicators(df, negative_cols):
    """
    Invert negative indicators so that higher values mean better performance.
    For each negative indicator, subtract the normalized value from 1.
    """
    df_adjusted = df.copy()
    for col in negative_cols:
        df_adjusted[col] = 1 - df_adjusted[col]
    return df_adjusted


def get_pca_weights(df, indicator_cols):
    """
    Get weights for each indicator using PCA on the adjusted data.
    If there is insufficient data, return equal weights.
    """
    features = df[indicator_cols]
    if features.shape[0] < 2:
        return np.ones(len(indicator_cols)) / len(indicator_cols)
    pca = PCA(n_components=1)
    pca.fit(features)
    # Use absolute loadings to ensure positive weights and then normalize.
    weights = np.abs(pca.components_[0])
    weights = weights / np.sum(weights)
    return weights


def compute_composite_score(df, indicator_cols, weights):
    """
    Compute the composite score for each record as the weighted sum of the indicators.
    """
    df = df.copy()
    df['composite_score'] = df[indicator_cols].dot(weights)
    return df


def rank_countries(df, year_col='year', score_col='composite_score'):
    """
    Rank countries within each year based on the composite score (highest score receives rank 1).
    """
    df = df.copy()
    df['rank'] = df.groupby(year_col)[score_col].rank(
        ascending=False, method='min')
    return df


def process_ranking_pipeline(df):
    """
    Process the entire ranking pipeline:
      1. Load data.
      2. Normalize indicators by year.
      3. Adjust negative indicators.
      4. For each year, derive PCA weights, compute composite score, and rank countries.
    Returns the final DataFrame with composite scores and ranks.
    """
    df.columns = df.columns.str.strip().str.lower()

    # Define indicator columns (ensure these column names match your CSV file):
    negative_cols = [
        'deaths',
        'incidence'
    ]

    positive_cols = [
        'medical doctors per 10,000',
        'nurses and midwifes per 10,000',
        'dentists per 10,000',
        'pharmacists per 10,000'
    ]
    indicator_cols = negative_cols + positive_cols

    # Step 2: Normalize the indicators for each year.
    df_normalized = normalize_data(df, indicator_cols, group_by='year')

    # Step 3: Adjust negative indicators so that higher values indicate better performance.
    df_adjusted = adjust_negative_indicators(df_normalized, negative_cols)

    # Process each year: compute PCA weights, composite score, and rank countries.
    final_results = pd.DataFrame()
    for _,group in df_adjusted.groupby('year'):
        group = group.copy()
        weights = get_pca_weights(group, indicator_cols)
        group = compute_composite_score(group, indicator_cols, weights)
        group = rank_countries(group, year_col='year',
                               score_col='composite_score')
        final_results = pd.concat([final_results, group], ignore_index=True)

    # Sort final results by year and then by rank.
    final_results = final_results.sort_values(
        ['year', 'rank']).reset_index(drop=True)
    return final_results


if __name__ == '__main__':
    # function above is being called in data_prep.py,
    # no module functionality needed
    print("This script is not meant to be run directly.")
