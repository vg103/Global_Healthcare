"""
Unit tests for the data preparation module healthcare.py
"""

import unittest
from unittest.mock import patch
import pandas as pd
from data_prep.healthcare import (
    import_data, pivot_ihme, drop_sex, ag_over_cause, reconcile_locations,
    make_medical_data_df, process_healthcare_data
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

        self.mock_pivot_ihme_data = pd.DataFrame({
            "location": ["Afghanistan", "Afghanistan"],
            "year": [1990, 1991],
            "Deaths": [456.5441080858281, 457.5592984646225],
            "Incidence": [1063.218329, 1075.179286]
            })

        self.med_df = pd.DataFrame({
            'ParentLocation': ['Africa', 'Africa'],
            'Location': ['Central African Republic', 'Chad'],
            'Period': [2023, 2023],
            'Value': [0.74, 0.85]
        })
        self.nurse_df = pd.DataFrame({
            'ParentLocation': ['Africa', 'Africa'],
            'Location': ['Central African Republic', 'Chad'],
            'Period': [2023, 2023],
            'Value': [10.97, 1.67]
        })
        self.pharm_df = pd.DataFrame({
            'ParentLocation': ['Africa', 'Africa'],
            'Location': ['Central African Republic', 'Chad'],
            'Period': [2023, 2023],
            'Value': [0.03, 0.08]
        })
        self.dent_df = pd.DataFrame({
            'ParentLocation': ['Africa', 'Africa'],
            'Location': ['Central African Republic', 'Chad'],
            'Period': [2023, 2023],
            'Value': [0.01, 0.01]
        })

        self.full_med_df = pd.DataFrame({
            "ParentLocation": ["Africa", "Africa"],
            "Location": ["Central African Republic", "Chad"],
            "Period": [2023, 2023],
            "Medical Doctors per 10,000": [0.74, 0.85],
            "Nurses and Midwifes per 10,000": [10.97, 1.67],
            "Pharmacists per 10,000": [0.03, 0.08],
            "Dentists per 10,000": [0.01, 0.01]
            })

    @patch("pandas.read_csv")
    def test_df_exists(self, mock_read_csv):
        """Test that the DataFrame is not empty after importing data."""
        mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2, 3]})
        df = import_data(data_path="test_path.csv")
        self.assertGreater(df.shape[0], 0, "data is empty")

    @patch("data_prep.healthcare.pd.DataFrame.to_csv")
    def test_pivot_ihme(self, mock_to_csv):
        """Test pivot_ihme function"""
        pivoted = pivot_ihme(self.mock_ihme_data)
        self.assertIn('Deaths', pivoted.columns)
        self.assertNotIn('measure', pivoted.columns)

    def test_drop_sex(self):
        """Test drop_sex function"""
        df_no_sex = drop_sex(self.mock_ihme_data)
        self.assertNotIn('sex', df_no_sex.columns)
        self.assertEqual(len(df_no_sex), 1)

    def test_ag_over_cause(self):
        """Test ag_over_cause function"""
        df_agg = ag_over_cause(self.mock_ihme_data)
        self.assertNotIn('cause', df_agg.columns)
        self.assertIn('location', df_agg.columns)
        self.assertIn('year', df_agg.columns)

    def test_make_medical_data_df(self):
        """Test make_medical_data_df function"""
        merged_df = make_medical_data_df(self.med_df, self.nurse_df, self.pharm_df, self.dent_df)
        self.assertEqual(merged_df.shape[1], 7)
        self.assertIn('Medical Doctors per 10,000', merged_df.columns)

    @patch("data_prep.healthcare.import_data")
    @patch("data_prep.healthcare.make_medical_data_df")
    @patch("data_prep.healthcare.pivot_ihme")
    @patch("data_prep.healthcare.drop_sex")
    @patch("data_prep.healthcare.ag_over_cause")
    @patch("pandas.DataFrame.to_csv")
    def test_process_healthcare_data(self, mock_to_csv, mock_ag_over_cause, mock_drop_sex,
                                     mock_pivot_ihme, mock_make_medical_data_df, mock_import_data):
        """Test that process_healthcare_data runs without errors and produces expected calls."""
        mock_import_data.return_value = self.mock_ihme_data
        mock_pivot_ihme.return_value = self.mock_pivot_ihme_data
        mock_make_medical_data_df.return_value = self.full_med_df
        mock_drop_sex.return_value = mock_pivot_ihme.return_value
        mock_ag_over_cause.return_value = mock_pivot_ihme.return_value

        process_healthcare_data("test_path/")

        mock_pivot_ihme.assert_called_once()
        mock_drop_sex.assert_called_once()
        mock_ag_over_cause.assert_called_once()
        mock_to_csv.assert_called()

if __name__ == '__main__':
    unittest.main()
