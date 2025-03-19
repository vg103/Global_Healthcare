"""
Tests for the hcare.ranking module.

Validates normalization, negative indicator adjustment, PCA weighting,
composite scoring, country ranking, and the complete pipeline.
"""

import unittest
import pandas as pd
import numpy as np
from hcare import ranking


class TestRanking(unittest.TestCase):
    """Unit tests for ranking functions in hcare.ranking."""

    def setUp(self):
        """Initialize a sample DataFrame for testing."""
        self.sample_data = pd.DataFrame({
            'year': [2000, 2000, 2001, 2001],
            'country': ['A', 'B', 'A', 'B'],
            'deaths': [100, 200, 150, 250],
            'incidence': [300, 400, 350, 450],
            'medical doctors per 10,000': [10, 20, 15, 25],
            'nurses and midwifes per 10,000': [20, 30, 25, 35],
            'dentists per 10,000': [30, 40, 35, 45],
            'pharmacists per 10,000': [40, 50, 45, 55],
        })

    def test_normalize_data(self):
        """Verify that normalization scales indicators to [0, 1] per year."""
        indicator_cols = [
            'deaths', 'incidence',
            'medical doctors per 10,000',
            'nurses and midwifes per 10,000',
            'dentists per 10,000', 'pharmacists per 10,000'
        ]
        df_norm = ranking.normalize_data(
            self.sample_data, indicator_cols, group_by='year'
        )
        for year, group in df_norm.groupby('year'):
            for col in indicator_cols:
                self.assertAlmostEqual(
                    group[col].min(), 0.0,
                    msg=f"In {year}, {col} min is not 0"
                )
                self.assertAlmostEqual(
                    group[col].max(), 1.0,
                    msg=f"In {year}, {col} max is not 1"
                )

    def test_adjust_negative_indicators(self):
        """Verify negative indicators are inverted (1 - value)."""
        indicator_cols = [
            'deaths', 'incidence',
            'medical doctors per 10,000',
            'nurses and midwifes per 10,000',
            'dentists per 10,000', 'pharmacists per 10,000'
        ]
        negative_cols = ['deaths', 'incidence']
        df_norm = ranking.normalize_data(
            self.sample_data, indicator_cols, group_by='year'
        )
        df_adj = ranking.adjust_negative_indicators(df_norm, negative_cols)
        for col in negative_cols:
            for year, group in df_norm.groupby('year'):
                orig_vals = group[col].values
                adj_vals = df_adj[df_adj['year'] == year][col].values
                for orig, adj in zip(orig_vals, adj_vals):
                    self.assertAlmostEqual(
                        adj, 1 - orig,
                        msg=f"{col} in {year} not adjusted properly."
                    )

    def test_get_pca_weights(self):
        """Verify PCA weights sum to 1 and are non-negative."""
        indicator_cols = ['col1', 'col2', 'col3']
        data = {
            'col1': [0.2, 0.8],
            'col2': [0.3, 0.7],
            'col3': [0.5, 0.5]
        }
        df = pd.DataFrame(data)
        weights = ranking.get_pca_weights(df, indicator_cols)
        self.assertAlmostEqual(
            np.sum(weights), 1.0, msg="PCA weights do not sum to 1."
        )
        self.assertTrue(
            np.all(weights >= 0), msg="Negative PCA weight found."
        )
        # Test edge case: single-row input
        df_single = pd.DataFrame({col: [0.5] for col in indicator_cols})
        weights_single = ranking.get_pca_weights(df_single, indicator_cols)
        expected = np.ones(len(indicator_cols)) / len(indicator_cols)
        np.testing.assert_allclose(
            weights_single, expected,
            err_msg="Single-row weights are not uniform."
        )

    def test_compute_composite_score(self):
        """Verify composite scores are computed as weighted dot products."""
        indicator_cols = ['a', 'b', 'c']
        data = {
            'a': [0.1, 0.4],
            'b': [0.2, 0.5],
            'c': [0.3, 0.6]
        }
        df = pd.DataFrame(data)
        weights = np.array([0.2, 0.3, 0.5])
        df_scored = ranking.compute_composite_score(
            df, indicator_cols, weights)
        expected = df[indicator_cols].dot(weights)
        np.testing.assert_allclose(
            df_scored['composite_score'], expected,
            err_msg="Composite score mismatch."
        )

    def test_rank_countries(self):
        """Verify ranking assigns rank 1 to the highest composite scores."""
        data = {
            'year': [2000, 2000, 2000],
            'composite_score': [0.5, 0.8, 0.8],
            'country': ['A', 'B', 'C']
        }
        df = pd.DataFrame(data)
        df_ranked = ranking.rank_countries(
            df, year_col='year', score_col='composite_score'
        )
        for _, row in df_ranked.iterrows():
            if row['composite_score'] == 0.8:
                self.assertEqual(
                    row['rank'], 1,
                    msg=f"Country {row['country']} with score 0.8 should be rank 1."
                )
            elif row['composite_score'] == 0.5:
                self.assertEqual(
                    row['rank'], 3,
                    msg=f"Country {row['country']} with score 0.5 should be rank 3."
                )

    def test_process_ranking_pipeline(self):
        """
        Verify the full pipeline adds 'composite_score' and 'rank'
        and that the output is sorted correctly.
        """
        df_result = ranking.process_ranking_pipeline(self.sample_data)
        self.assertIn(
            'composite_score', df_result.columns,
            msg="Missing 'composite_score' column."
        )
        self.assertIn(
            'rank', df_result.columns,
            msg="Missing 'rank' column."
        )
        sorted_df = df_result.sort_values(
            ['year', 'rank']).reset_index(drop=True)
        pd.testing.assert_frame_equal(df_result, sorted_df, check_dtype=False)


if __name__ == '__main__':
    unittest.main()
