import unittest
import pandas as pd
import numpy as np
from hcare import ranking


class TestRanking(unittest.TestCase):

    def setUp(self):
        # Sample data fixture
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
        indicator_cols = [
            'deaths',
            'incidence',
            'medical doctors per 10,000',
            'nurses and midwifes per 10,000',
            'dentists per 10,000',
            'pharmacists per 10,000'
        ]
        df_normalized = ranking.normalize_data(
            self.sample_data, indicator_cols, group_by='year')
        for year, group in df_normalized.groupby('year'):
            for col in indicator_cols:
                self.assertAlmostEqual(group[col].min(), 0.0,
                                       msg=f"In year {year}, {col} min is not 0")
                self.assertAlmostEqual(group[col].max(), 1.0,
                                       msg=f"In year {year}, {col} max is not 1")

    def test_adjust_negative_indicators(self):
        indicator_cols = [
            'deaths',
            'incidence',
            'medical doctors per 10,000',
            'nurses and midwifes per 10,000',
            'dentists per 10,000',
            'pharmacists per 10,000'
        ]
        negative_cols = ['deaths', 'incidence']
        df_normalized = ranking.normalize_data(
            self.sample_data, indicator_cols, group_by='year')
        df_adjusted = ranking.adjust_negative_indicators(
            df_normalized, negative_cols)
        for col in negative_cols:
            for year, group in df_normalized.groupby('year'):
                original_vals = group[col].values
                adjusted_vals = df_adjusted[df_adjusted['year']
                                            == year][col].values
                for orig, adj in zip(original_vals, adjusted_vals):
                    self.assertAlmostEqual(adj, 1 - orig,
                                           msg=f"Column {col} in year {year} not properly adjusted.")

    def test_get_pca_weights(self):
        indicator_cols = ['col1', 'col2', 'col3']
        data = {
            'col1': [0.2, 0.8],
            'col2': [0.3, 0.7],
            'col3': [0.5, 0.5]
        }
        df = pd.DataFrame(data)
        weights = ranking.get_pca_weights(df, indicator_cols)
        self.assertAlmostEqual(np.sum(weights), 1.0,
                               msg="PCA weights do not sum to 1.")
        self.assertTrue(np.all(weights >= 0),
                        msg="Some PCA weights are negative.")

        # Edge case: only one row of data.
        df_single = pd.DataFrame({col: [0.5] for col in indicator_cols})
        weights_single = ranking.get_pca_weights(df_single, indicator_cols)
        expected_weights = np.ones(len(indicator_cols)) / len(indicator_cols)
        np.testing.assert_allclose(weights_single, expected_weights,
                                   err_msg="Weights for single row are not equal weights.")

    def test_compute_composite_score(self):
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
        expected_scores = df[indicator_cols].dot(weights)
        np.testing.assert_allclose(df_scored['composite_score'], expected_scores,
                                   err_msg="Composite score does not match expected values.")

    def test_rank_countries(self):
        data = {
            'year': [2000, 2000, 2000],
            'composite_score': [0.5, 0.8, 0.8],
            'country': ['A', 'B', 'C']
        }
        df = pd.DataFrame(data)
        df_ranked = ranking.rank_countries(
            df, year_col='year', score_col='composite_score')
        for _, row in df_ranked.iterrows():
            if row['composite_score'] == 0.8:
                self.assertEqual(row['rank'], 1,
                                 msg=f"Country {row['country']} with score 0.8 should have rank 1.")
            elif row['composite_score'] == 0.5:
                self.assertEqual(row['rank'], 3,
                                 msg=f"Country {row['country']} with score 0.5 should have rank 3.")

    def test_process_ranking_pipeline(self):
        df_result = ranking.process_ranking_pipeline(self.sample_data)
        self.assertIn('composite_score', df_result.columns,
                      msg="Output missing 'composite_score' column.")
        self.assertIn('rank', df_result.columns,
                      msg="Output missing 'rank' column.")
        sorted_df = df_result.sort_values(
            ['year', 'rank']).reset_index(drop=True)
        pd.testing.assert_frame_equal(df_result, sorted_df, check_dtype=False)


if __name__ == '__main__':
    unittest.main()
