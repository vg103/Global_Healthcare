import unittest
import numpy as np
from data_prep import data_prep

class TestDataPrep(unittest.TestCase):
    def test_df_exists(self):
        df = data_prep(data_path="data/data.csv")
        num_rows = len(df.shape[0])
        self.assertGreater(num_rows, 0, "data is empty")

        
if __name__ == '__main__':
    unittest.main()
        
        
# suite = unittest.TestLoader().loadTestsFromTestCase(UnitTests)
# _ = unittest.TextTestRunner().run(suite)
