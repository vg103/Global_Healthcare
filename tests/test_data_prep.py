import unittest
import numpy as np
from data_prep.data_prep import import_data

class TestDataPrep(unittest.TestCase):
    def test_df_exists(self):
        df = import_data(data_path="data/scraped_doc.csv")
        num_rows = df.shape[0]
        self.assertGreater(num_rows, 0, "data is empty")

        
if __name__ == '__main__':
    unittest.main()
        
        
# suite = unittest.TestLoader().loadTestsFromTestCase(UnitTests)
# _ = unittest.TextTestRunner().run(suite)
