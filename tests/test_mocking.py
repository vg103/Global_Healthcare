from hcare import data_prep, ranking
from hcare.hcare import (
    load_data,
    plot_compscore_over_time,
    plot_death_vs_docs,
    plot_ihme_data,
    plot_who_data,
    plot_metrics_by_country,
    plot_metrics_over_time,
    country_spider,
)
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Adjust sys.path so that the project root is on the path.
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Import functions from your modules.


class TestDataPrep(unittest.TestCase):
    def setUp(self):
        self.ihme_df = pd.DataFrame({
            'location': ['CountryA', 'CountryA', 'CountryB', 'CountryB'],
            'sex': ['Both', 'Male', 'Both', 'Male'],
            'cause': ['Cause1', 'Cause1', 'Cause2', 'Cause2'],
            'year': [2000, 2000, 2001, 2001],
            'measure': ['death', 'incidence', 'death', 'incidence'],
            'val': [10, 5, 20, 15]
        })

    def test_pivot_ihme(self):
        pivoted = data_prep.pivot_ihme(self.ihme_df)
        self.assertIn('death_rate', pivoted.columns)
        self.assertIn('incidence_rate', pivoted.columns)
        self.assertEqual(len(pivoted), 4)

    def test_drop_sex(self):
        df = self.ihme_df.copy()
        df = pd.concat([df, pd.DataFrame([{'location': 'CountryC', 'sex': 'Both', 'cause': 'Cause3',
                                           'year': 2002, 'measure': 'death', 'val': 30}])], ignore_index=True)
        dropped = data_prep.drop_sex(df)
        self.assertNotIn('sex', dropped.columns)
        self.assertTrue((dropped['location'] == 'CountryC').any())

    def test_ag_over_cause(self):
        df = pd.DataFrame({
            'location': ['CountryA', 'CountryA'],
            'year': [2000, 2000],
            'cause': ['Cause1', 'Cause1'],
            'death_rate': [10, 20]
        })
        agged = data_prep.ag_over_cause(df)
        self.assertEqual(len(agged), 1)
        self.assertEqual(agged.iloc[0]['death_rate'], 30)


class TestRanking(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'deaths': [10, 20, 5, 15],
            'incidence': [1, 2, 1, 2],
            'medical doctors per 10,000': [30, 40, 35, 45],
            'nurses and midwifes per 10,000': [50, 60, 55, 65],
            'dentists per 10,000': [5, 6, 7, 8],
            'pharmacists per 10,000': [2, 3, 2.5, 3.5],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB']
        })
        self.df.columns = [col.strip().lower() for col in self.df.columns]

    def test_normalize_data(self):
        indicator_cols = ['deaths', 'incidence', 'medical doctors per 10,000',
                          'nurses and midwifes per 10,000', 'dentists per 10,000', 'pharmacists per 10,000']
        normalized = ranking.normalize_data(
            self.df, indicator_cols, group_by='year')
        self.assertEqual(normalized.shape, self.df.shape)

    def test_adjust_negative_indicators(self):
        df_copy = self.df.copy()
        negative_cols = ['deaths', 'incidence']
        adjusted = ranking.adjust_negative_indicators(df_copy, negative_cols)
        for col in negative_cols:
            np.testing.assert_array_almost_equal(
                adjusted[col], 1 - self.df[col])

    def test_get_pca_weights(self):
        indicator_cols = ['deaths', 'incidence', 'medical doctors per 10,000',
                          'nurses and midwifes per 10,000', 'dentists per 10,000', 'pharmacists per 10,000']
        weights = ranking.get_pca_weights(self.df, indicator_cols)
        self.assertEqual(len(weights), len(indicator_cols))
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)

    def test_compute_composite_score_and_rank(self):
        indicator_cols = ['deaths', 'incidence', 'medical doctors per 10,000',
                          'nurses and midwifes per 10,000', 'dentists per 10,000', 'pharmacists per 10,000']
        weights = np.ones(len(indicator_cols)) / len(indicator_cols)
        scored_df = ranking.compute_composite_score(
            self.df, indicator_cols, weights)
        self.assertIn('composite_score', scored_df.columns)
        ranked_df = ranking.rank_countries(
            scored_df, year_col='year', score_col='composite_score')
        self.assertIn('rank', ranked_df.columns)

    def test_process_ranking_pipeline(self):
        result_df = ranking.process_ranking_pipeline(self.df.copy())
        self.assertIn('composite_score', result_df.columns)
        self.assertIn('rank', result_df.columns)
        self.assertTrue(set(result_df['year']) == {2000, 2001})


class TestHCare(unittest.TestCase):
    def setUp(self):
        self.df_metrics = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
            'composite_score': [0.5, 0.7, 0.6, 0.8],
            'medical_doctors_per_10000': [30, 40, 35, 45],
            'nurses_midwifes_per_10000': [50, 60, 55, 65],
            'deaths': [10, 20, 5, 15]
        })

        self.df_IHME = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
            'cause': ['Cause1', 'Cause1', 'Cause2', 'Cause2'],
            'deaths': [10, 20, 5, 15],
            'incidence': [1, 2, 1, 2],
            'sex': ['Both', 'Both', 'Both', 'Both']
        })

        # Note: Changed column name from "region" to "Region" to match hcare expectations.
        self.df_WHO = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
            'Region': ['Region1', 'Region1', 'Region2', 'Region2'],
            'medical_doctors_per_10000': [30, 40, 35, 45],
            'nurses_midwifes_per_10000': [50, 60, 55, 65],
            'pharmacists_per_10000': [2, 3, 2.5, 3.5],
            'dentists_per_10000': [5, 6, 7, 8]
        })

    @patch('hcare.hcare.process_healthcare_data')
    def test_load_data(self, mock_process):
        mock_process.return_value = (
            self.df_IHME.copy(), self.df_WHO.copy(), self.df_metrics.copy())
        df_ihme, df_who, df_metrics = load_data()
        self.assertIn('location', df_ihme.columns)
        self.assertIn('Region', df_who.columns)
        self.assertTrue(
            'composite_score' in df_metrics.columns or 'rank' in df_metrics.columns)

    def test_plot_compscore_over_time(self):
        fig = plot_compscore_over_time(
            self.df_metrics, primary_metric="composite_score", selected_location=['CountryA'])
        self.assertIsInstance(fig, go.Figure)

    def test_plot_death_vs_docs(self):
        fig = plot_death_vs_docs(self.df_metrics, primary_metric="deaths",
                                 secondary_metric="medical_doctors_per_10000", selected_location=['CountryB'])
        self.assertIsInstance(fig, go.Figure)

    def test_plot_ihme_data(self):
        fig = plot_ihme_data(self.df_IHME, metric="deaths", selected_year=2000, selected_location=[
                             'CountryA'], selected_cause=['Cause1'], selected_sex=['Both'])
        self.assertIsInstance(fig, go.Figure)

    def test_plot_who_data(self):
        fig = plot_who_data(self.df_WHO, selected_year=2000, selected_location=[
                            'CountryA'], selected_regions=['Region1'])
        self.assertIsInstance(fig, go.Figure)

    def test_plot_metrics_by_country(self):
        fig = plot_metrics_by_country(self.df_metrics, primary_metric="medical_doctors_per_10000",
                                      secondary_metric="nurses_midwifes_per_10000", selected_year=2000, selected_location=['CountryA'])
        self.assertIsInstance(fig, go.Figure)

    def test_plot_metrics_over_time(self):
        fig = plot_metrics_over_time(self.df_metrics, primary_metric="medical_doctors_per_10000",
                                     secondary_metric="nurses_midwifes_per_10000", selected_location=['CountryB'])
        self.assertIsInstance(fig, go.Figure)

    def test_country_spider(self):
        fig = country_spider(self.df_WHO, 'CountryA', 2000)
        self.assertIsInstance(fig, go.Figure)


if __name__ == '__main__':
    unittest.main()
