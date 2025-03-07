"""
Unit tests for the data preparation module.
"""

import unittest
from data_prep.data_prep import import_data


class TestDataPrep(unittest.TestCase):
    """Test cases for the data preparation functions."""

    def test_df_exists(self):
        """Test that the DataFrame is not empty after importing data."""
        df = import_data(data_path="data/scraped_doc.csv")
        num_rows = df.shape[0]
        self.assertGreater(num_rows, 0, "data is empty")


if __name__ == '__main__':
    unittest.main()
