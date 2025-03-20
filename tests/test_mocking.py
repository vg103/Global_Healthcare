#!/usr/bin/env python3
"""
Unit tests for the hcare project modules.
"""
import os
import sys
import unittest
from unittest.mock import patch

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from hcare import data_prep, ranking
from hcare.hcare import (
    load_data, plot_compscore_over_time, plot_death_vs_docs, plot_ihme_data,
    plot_who_data, plot_metrics_by_country, plot_metrics_over_time,
    country_spider,
)
# Local (first-party) imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)
# Standard library imports

class TestDataPrep(unittest.TestCase):
    """Tests for data preparation functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.ihme_df = pd.DataFrame({
            'location': ['CountryA', 'CountryA', 'CountryB', 'CountryB'],
            'sex': ['Both', 'Male', 'Both', 'Male'],
            'cause': ['Cause1', 'Cause1', 'Cause2', 'Cause2'],
            'year': [2000, 2000, 2001, 2001],
            'measure': ['death', 'incidence', 'death', 'incidence'],
            'val': [10, 5, 20, 15],
        })

    def test_pivot_ihme(self):
        """Test pivoting IHME data."""
        pivoted = data_prep.pivot_ihme(self.ihme_df)
        self.assertIn('death_rate', pivoted.columns)
        self.assertIn('incidence_rate', pivoted.columns)
        self.assertEqual(len(pivoted), 4)

    def test_drop_sex(self):
        """Test dropping the 'sex' column."""
        df = self.ihme_df.copy()
        extra_row = pd.DataFrame([{
            'location': 'CountryC',
            'sex': 'Both',
            'cause': 'Cause3',
            'year': 2002,
            'measure': 'death',
            'val': 30,
        }])
        df = pd.concat([df, extra_row], ignore_index=True)
        dropped = data_prep.drop_sex(df)
        self.assertNotIn('sex', dropped.columns)
        self.assertTrue((dropped['location'] == 'CountryC').any())

    def test_ag_over_cause(self):
        """Test aggregation over cause."""
        df = pd.DataFrame({
            'location': ['CountryA', 'CountryA'],
            'year': [2000, 2000],
            'cause': ['Cause1', 'Cause1'],
            'death_rate': [10, 20],
        })
        agged = data_prep.ag_over_cause(df)
        self.assertEqual(len(agged), 1)
        self.assertEqual(agged.iloc[0]['death_rate'], 30)


class TestRanking(unittest.TestCase):
    """Tests for ranking functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.df = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'deaths': [10, 20, 5, 15],
            'incidence': [1, 2, 1, 2],
            'medical doctors per 10,000': [30, 40, 35, 45],
            'nurses and midwifes per 10,000': [50, 60, 55, 65],
            'dentists per 10,000': [5, 6, 7, 8],
            'pharmacists per 10,000': [2, 3, 2.5, 3.5],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
        })
        self.df.columns = [col.strip().lower() for col in self.df.columns]

    def test_normalize_data(self):
        """Test normalization of data by year."""
        indicator_cols = [
            'deaths', 'incidence', 'medical doctors per 10,000',
            'nurses and midwifes per 10,000', 'dentists per 10,000',
            'pharmacists per 10,000'
        ]
        normalized = ranking.normalize_data(
            self.df, indicator_cols, group_by='year'
        )
        self.assertEqual(normalized.shape, self.df.shape)

    def test_adjust_negative_indicators(self):
        """Test adjustment of negative indicators."""
        df_copy = self.df.copy()
        negative_cols = ['deaths', 'incidence']
        adjusted = ranking.adjust_negative_indicators(df_copy, negative_cols)
        for col in negative_cols:
            np.testing.assert_array_almost_equal(
                adjusted[col], 1 - self.df[col]
            )

    def test_get_pca_weights(self):
        """Test computing PCA weights."""
        indicator_cols = [
            'deaths', 'incidence', 'medical doctors per 10,000',
            'nurses and midwifes per 10,000', 'dentists per 10,000',
            'pharmacists per 10,000'
        ]
        weights = ranking.get_pca_weights(self.df, indicator_cols)
        self.assertEqual(len(weights), len(indicator_cols))
        self.assertAlmostEqual(np.sum(weights), 1.0, places=5)

    def test_compute_composite_score_and_rank(self):
        """Test composite score computation and ranking."""
        indicator_cols = [
            'deaths', 'incidence', 'medical doctors per 10,000',
            'nurses and midwifes per 10,000', 'dentists per 10,000',
            'pharmacists per 10,000'
        ]
        weights = np.ones(len(indicator_cols)) / len(indicator_cols)
        scored_df = ranking.compute_composite_score(
            self.df, indicator_cols, weights
        )
        self.assertIn('composite_score', scored_df.columns)
        ranked_df = ranking.rank_countries(
            scored_df, year_col='year', score_col='composite_score'
        )
        self.assertIn('rank', ranked_df.columns)

    def test_process_ranking_pipeline(self):
        """Test the complete ranking pipeline."""
        result_df = ranking.process_ranking_pipeline(self.df.copy())
        self.assertIn('composite_score', result_df.columns)
        self.assertIn('rank', result_df.columns)
        self.assertEqual(set(result_df['year']), {2000, 2001})


class TestHCare(unittest.TestCase):
    """Tests for hcare visualization and data loading functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.df_metrics = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
            'composite_score': [0.5, 0.7, 0.6, 0.8],
            'medical_doctors_per_10000': [30, 40, 35, 45],
            'nurses_midwifes_per_10000': [50, 60, 55, 65],
            'deaths': [10, 20, 5, 15],
        })
        self.df_ihme = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
            'cause': ['Cause1', 'Cause1', 'Cause2', 'Cause2'],
            'deaths': [10, 20, 5, 15],
            'incidence': [1, 2, 1, 2],
            'sex': ['Both', 'Both', 'Both', 'Both'],
        })
        # Changed column name from "region" to "Region" to match hcare expectations.
        self.df_who = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'location': ['CountryA', 'CountryB', 'CountryA', 'CountryB'],
            'Region': ['Region1', 'Region1', 'Region2', 'Region2'],
            'medical_doctors_per_10000': [30, 40, 35, 45],
            'nurses_midwifes_per_10000': [50, 60, 55, 65],
            'pharmacists_per_10000': [2, 3, 2.5, 3.5],
            'dentists_per_10000': [5, 6, 7, 8],
        })

    @patch('hcare.hcare.process_healthcare_data')
    def test_load_data(self, mock_process):
        """Test data loading with a mocked process."""
        mock_process.return_value = (
            self.df_ihme.copy(), self.df_who.copy(), self.df_metrics.copy()
        )
        df_ihme_loaded, df_who_loaded, df_metrics = load_data()
        self.assertIn('location', df_ihme_loaded.columns)
        self.assertIn('Region', df_who_loaded.columns)
        self.assertTrue(
            'composite_score' in df_metrics.columns or 'rank' in df_metrics.columns
        )

    def test_plot_compscore_over_time(self):
        """Test plotting composite score over time."""
        fig = plot_compscore_over_time(
            self.df_metrics,
            primary_metric="composite_score",
            selected_location=['CountryA']
        )
        self.assertIsInstance(fig, go.Figure)

    def test_plot_death_vs_docs(self):
        """Test plotting deaths versus medical doctors."""
        fig = plot_death_vs_docs(
            self.df_metrics,
            primary_metric="deaths",
            secondary_metric="medical_doctors_per_10000",
            selected_location=['CountryB']
        )
        self.assertIsInstance(fig, go.Figure)

    def test_plot_ihme_data(self):
        """Test plotting IHME data."""
        fig = plot_ihme_data(
            self.df_ihme,
            metric="deaths",
            select_yr_and_sex=(2000,['Both']),
            selected_location=['CountryA'],
            selected_cause=['Cause1'],
        )
        self.assertIsInstance(fig, go.Figure)

    def test_plot_who_data(self):
        """Test plotting WHO data."""
        fig = plot_who_data(
            self.df_who,
            select_year=2000,
            selected_location=['CountryA'],
            selected_regions=['Region1']
        )
        self.assertIsInstance(fig, go.Figure)

    def test_plot_metrics_by_country(self):
        """Test plotting metrics by country."""
        fig = plot_metrics_by_country(
            self.df_metrics,
            primary_metric="medical_doctors_per_10000",
            secondary_metric="nurses_midwifes_per_10000",
            selected_yr=2000,
            selected_place=(['CountryA'],None)
        )
        self.assertIsInstance(fig, go.Figure)

    def test_plot_metrics_over_time(self):
        """Test plotting metrics over time."""
        fig = plot_metrics_over_time(
            self.df_metrics,
            primary_metric="medical_doctors_per_10000",
            secondary_metric="nurses_midwifes_per_10000",
            selected_location=['CountryB']
        )
        self.assertIsInstance(fig, go.Figure)

    def test_country_spider(self):
        """Test the country spider plot."""
        fig = country_spider(self.df_who, 'CountryA', 2000)
        self.assertIsInstance(fig, go.Figure)


if __name__ == '__main__':
    unittest.main()
