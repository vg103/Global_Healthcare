"""
Unit tests for the data preparation module data_prep.py
"""
import unittest
from unittest.mock import patch
import pandas as pd
from hcare.data_prep import (
    import_data, pivot_ihme, drop_sex, ag_over_cause, reconcile_locations,
    make_medical_data_df, process_healthcare_data
)


class TestHealthcare(unittest.TestCase):
    """Test cases for the data preparation functions."""

    def setUp(self):
        """Set up mock data for testing with matching merge keys."""
        # Adjusted IHME mock data so that the merge keys match the WHO data below.
        self.mock_ihme_data = pd.DataFrame({
            'measure': ['Deaths', 'Deaths'],
            'location': ['Central African Republic', 'Central African Republic'],
            'sex': ['Male', 'Female'],
            'age': ['All ages', 'All ages'],
            'cause': ['Cardiovascular diseases', 'Cardiovascular diseases'],
            'metric': ['Rate', 'Rate'],
            'year': [2023, 2023],
            'val': [456.54, 457.56],
            'upper': [460.00, 461.00],
            'lower': [450.00, 455.00]
        })

        # Pivoted IHME data (simulate a successful pivot); using matching keys.
        self.mock_pivot_ihme_data = pd.DataFrame({
            "location": ["Central African Republic"],
            "sex": ["Both"],
            "cause": ["Cardiovascular diseases"],
            "year": [2023],
            "Deaths": [456.54],
            "Incidence": [1063.22]
        })

        # WHO data: both keys match the pivoted IHME data ("Central African Republic", 2023)
        self.med_df = pd.DataFrame({
            'ParentLocation': ['Africa'],
            'Location': ['Central African Republic'],
            'Period': [2023],
            'Value': [0.74]
        })
        self.nurse_df = pd.DataFrame({
            'ParentLocation': ['Africa'],
            'Location': ['Central African Republic'],
            'Period': [2023],
            'Value': [10.97]
        })
        self.pharm_df = pd.DataFrame({
            'ParentLocation': ['Africa'],
            'Location': ['Central African Republic'],
            'Period': [2023],
            'Value': [0.03]
        })
        self.dent_df = pd.DataFrame({
            'ParentLocation': ['Africa'],
            'Location': ['Central African Republic'],
            'Period': [2023],
            'Value': [0.01]
        })

        self.full_med_df = pd.DataFrame({
            "ParentLocation": ["Africa"],
            "Location": ["Central African Republic"],
            "Period": [2023],
            "Medical Doctors per 10,000": [0.74],
            "Nurses and Midwifes per 10,000": [10.97],
            "Pharmacists per 10,000": [0.03],
            "Dentists per 10,000": [0.01]
        })

    @patch("pandas.read_csv")
    def test_df_exists(self, mock_read_csv):
        """Test that the DataFrame is not empty after importing data."""
        mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2, 3]})
        df = import_data(data_path="test_path.csv")
        self.assertGreater(df.shape[0], 0, "data is empty")

    @patch("hcare.data_prep.pd.DataFrame.to_csv")
    def test_pivot_ihme(self, mock_to_csv):
        """Test pivot_ihme function"""
        pivoted = pivot_ihme(self.mock_ihme_data)
        self.assertIn('Deaths', pivoted.columns)
        self.assertNotIn('measure', pivoted.columns)

    def test_drop_sex(self):
        """Test drop_sex function"""
        df_no_sex = drop_sex(self.mock_ihme_data)
        # With two rows (Male and Female) dropped, only one row remains if one row had "Both"
        # For this test, we can check that 'sex' column is removed.
        self.assertNotIn('sex', df_no_sex.columns)

    def test_ag_over_cause(self):
        """Test ag_over_cause function"""
        df_agg = ag_over_cause(self.mock_ihme_data)
        self.assertIn('location', df_agg.columns)
        self.assertIn('year', df_agg.columns)
        self.assertNotIn('cause', df_agg.columns)

    def test_make_medical_data_df(self):
        """Test make_medical_data_df function"""
        merged_df = make_medical_data_df(
            self.med_df, self.nurse_df, self.pharm_df, self.dent_df)
        self.assertEqual(merged_df.shape[1], 7)
        self.assertIn('Medical Doctors per 10,000', merged_df.columns)

    @patch("hcare.data_prep.import_data")
    @patch("hcare.data_prep.make_medical_data_df")
    @patch("hcare.data_prep.pivot_ihme")
    @patch("hcare.data_prep.drop_sex")
    @patch("hcare.data_prep.ag_over_cause")
    def test_process_healthcare_data(self, mock_ag_over_cause, mock_drop_sex,
                                     mock_pivot_ihme, mock_make_medical_data_df, mock_import_data):
        """Test that process_healthcare_data runs without errors and produces expected calls."""
        # Set up the mocks so that merge keys match:
        mock_import_data.return_value = self.mock_ihme_data
        mock_pivot_ihme.return_value = self.mock_pivot_ihme_data
        mock_make_medical_data_df.return_value = self.full_med_df
        mock_drop_sex.return_value = self.mock_pivot_ihme_data
        mock_ag_over_cause.return_value = self.mock_pivot_ihme_data

        process_healthcare_data("test_path/")

        mock_pivot_ihme.assert_called_once()
        mock_drop_sex.assert_called_once()
        mock_ag_over_cause.assert_called_once()


if __name__ == '__main__':
    unittest.main()
