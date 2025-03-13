"""
Unit tests for the data preparation module healthcare.py
"""

import unittest
import pandas as pd
from data_prep.healthcare import (
    import_data, pivot_ihme, drop_sex, ag_over_cause, make_medical_data_df
)

class TestHealthcare(unittest.TestCase):
    """Test cases for the data preparation functions."""

    def setUp(self):
        """Set up mock data for testing"""
        self.mock_ihme_data = pd.DataFrame({
            'measure': ['Deaths', 'Deaths', 'Deaths', 'Deaths', 'Deaths'],
            'location': ['Malawi', 'Malawi', 'Malawi', 'Malawi', 'Malawi'],
            'sex': ['Male', 'Female', 'Both', 'Male', 'Female'],
            'age': ['All ages', 'All ages', 'All ages', 'All ages', 'All ages'],
            'cause': ['Neurological disorders', 'Neurological disorders', 'Neurological disorders',
                       'Mental disorders', 'Mental disorders'],
            'metric': ['Rate', 'Rate', 'Rate', 'Rate', 'Rate'],
            'year': [1980, 1980, 1980, 1980, 1980],
            'val': [13.86130132844103, 11.18627671841312, 12.48205573563055,
                    2.3363112179351145e-06, 3.4283324156317983e-06],
            'upper': [20.339947884396192, 20.66255073478848, 20.860054735272126,
                      3.506245007981233e-06, 1.0543626360124419e-05],
            'lower': [9.461606326, 6.410529068994913, 8.355745837273847,
                      9.98065613804026e-09, 4.397253535704954e-07]
        })

        self.med_df = pd.DataFrame({
            'Location': ['Central African Republic', 'Chad', 'Senegal', "Cote d'Ivoire", 'Nepal'],
            'Period': [2023, 2023, 2023, 2023, 2023],
            'Value': [0.74, 0.85, 1.09, 1.66, 10.11]
        })
        self.nurse_df = pd.DataFrame({
            'Location': ['Central African Republic', 'Chad', 'Senegal', "Cote d'Ivoire", 'Nepal'],
            'Period': [2023, 2023, 2023, 2023, 2023],
            'Value': [10.97, 1.67, 4.24, 7.93, 40.92]
        })
        self.pharm_df = pd.DataFrame({
            'Location': ['Central African Republic', 'Chad', 'Senegal', "Cote d'Ivoire", 'Nepal'],
            'Period': [2023, 2023, 2023, 2023, 2023],
            'Value': [0.03, 0.08, 0.2, 0.39, 2.25]
        })
        self.dent_df = pd.DataFrame({
            'Location': ['Central African Republic', 'Chad', 'Senegal', "Cote d'Ivoire", 'Nepal'],
            'Period': [2023, 2023, 2023, 2023, 2023],
            'Value': [0.01, 0.01, 0.11, 0.14, 1.64]
        })

    def test_df_exists(self):
        """Test that the DataFrame is not empty after importing data."""
        df = import_data(data_path="data_prep/final_data/inner_merged_data.csv")
        num_rows = df.shape[0]
        self.assertGreater(num_rows, 0, "data is empty")

    def test_pivot_ihme(self):
        """Test pivot_ihme function"""
        pivoted = pivot_ihme(self.mock_ihme_data)
        self.assertIn('death_rate', pivoted.columns)
        self.assertIn('incidence_rate', pivoted.columns)

    def test_drop_sex(self):
        """Test drop_sex function"""
        df_no_sex = drop_sex(self.mock_ihme_data)
        self.assertNotIn('sex', df_no_sex.columns)
        self.assertTrue(all(df_no_sex['location'] == 'Canada'))

    def test_ag_over_cause(self):
        """Test ag_over_cause function"""
        df_agg = ag_over_cause(self.mock_ihme_data)
        self.assertNotIn('cause', df_agg.columns)
        self.assertEqual(df_agg.shape[0], 2)

    def test_make_medical_data_df(self):
        """Test make_medical_data_df function"""
        merged_df = make_medical_data_df(self.med_df, self.nurse_df, self.pharm_df, self.dent_df)
        self.assertEqual(merged_df.shape[1], 6)
        self.assertIn('Medical Doctors per 10,000', merged_df.columns)


if __name__ == '__main__':
    unittest.main()
