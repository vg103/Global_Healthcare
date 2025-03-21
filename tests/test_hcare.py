"""
Unit tests for the streamlit dashboard generating module hcare.py
"""
import os
import sys

import unittest
from streamlit.testing.v1 import AppTest

# Ensure the hcare folder (which contains hcare.py and data_prep.py) is in the Python path.
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, "..", "hcare"))

class HcareTest(unittest.TestCase):
    """
    This class tests UI for hcare.py.
    """

    def setUp(self):
        """
        The unittest framework automatically runs this setUp function before each test.
        We initialize AppTest for the hcare.py file.
        """
        # pylint: disable=no-member
        self.at = AppTest.from_file(
            '../hcare/hcare.py', default_timeout=30).run()
        print("self.at is type: ", type(self.at))

    def test_title(self):
        """
        Tests the title of the dashboard.
        """
        self.assertEqual(self.at.title[0].value, "Global Healthcare")

    # Testing for Tab 1: Global Healthcare Systems - Ranking and Scores
    def test_selectbox_ranking_year_and_metric_home(self):
        """
        Check if the selectbox for ranking years in the Home tab is populated correctly.
        Check if the metric selectbox for the composite score over time graph is working.
        """
        years = sorted(self.at.selectbox(key="home_year").options)
        self.assertGreater(len(years), 0)

        expected_metrics = ["composite_score", "rank"]
        self.assertEqual(self.at.selectbox(
            key="home_metric").options, expected_metrics)

    def test_multiselect_home_loc_compscore(self):
        """
        Check the multiselect for selecting locations in the composite score over time 
        graph on the Home tab.
        """
        locations = sorted(self.at.multiselect(key="home_loc").options)
        self.assertGreater(len(locations), 0)

    def test_plot_compscore_home(self):
        """
        Check if the composite score plot is generated correctly in the Home tab.
        """
        chart = self.at.get('plotly_chart')[0]
        self.assertIsNotNone(chart)

    def test_multiselect_location_death_vs_doc(self):
        """
        Check the multiselect for selecting locations in the death vs doc graph on the Home tab.
        """
        locations = sorted(self.at.multiselect(key="country1").options)
        self.assertGreater(len(locations), 0)

    def test_plot_death_vs_doc_home(self):
        """
        Check if the death vs doc plot is generated correctly in the Home tab.
        """
        chart = self.at.get('plotly_chart')[1]
        self.assertIsNotNone(chart)


    # Testing for Tab 2: IHME Data Graph
    def test_selectbox_metric_and_year_ihme(self):
        """
        Check the selectbox for the metric choice in the IHME Data tab.
        Check if the years for IHME data are populated correctly.
        """
        self.assertEqual(self.at.selectbox(
            key="ihme_measure").options, ["deaths", "incidence"])

        years = sorted(self.at.selectbox(key="ihme_year").options)
        self.assertGreater(len(years), 0)

    def test_multiselect_location_ihme(self):
        """
        Check the multiselect for selecting locations in the IHME Data tab.
        """
        locations = sorted(self.at.multiselect(key="ihme_loc").options)
        self.assertGreater(len(locations), 0)

    def test_multiselect_cause_and_sex_ihme(self):
        """
        Check the multiselect for selecting causes in the IHME Data tab.
        Check the multiselect for selecting sex in the IHME Data tab.
        """
        causes = sorted(self.at.multiselect(key="ihm_cause").options)
        self.assertGreater(len(causes), 0)

        sexes = sorted(self.at.multiselect(key="ihm_sex").options)
        self.assertGreater(len(sexes), 0)

    def test_plot_ihme_data(self):
        """
        Check if the plot is generated correctly in the IHME Data tab.
        """
        chart = self.at.get('plotly_chart')[2]
        self.assertIsNotNone(chart)

    # Testing for Tab 3: WHO Data Graph
    def test_selectbox_year_who(self):
        """
        Check if the years for WHO data are populated correctly.
        """
        years_who = sorted(self.at.selectbox(key="who_year").options)
        self.assertGreater(len(years_who), 0)

    def test_plot_who_data(self):
        """
        Check if the plot is generated correctly in the WHO Data tab.
        """
        chart = self.at.get('plotly_chart')[3]
        self.assertIsNotNone(chart)

    # Testing for Tab 4: Metrics By Country Graph
    def test_selectbox_both_metrics_and_year_country(self):
        """
        Check if the primary metric selectbox for the Metrics by Country tab is working.
        Check if the secondary metric selectbox for the Metrics by Country tab is working.
        Check if the years for the Metrics by Country tab are populated correctly.
        """
        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(
            key="country_met_one").options, metrics)

        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(
            key="country_met_two").options, metrics)

        years = sorted(self.at.selectbox(key="country_year").options)
        self.assertGreater(len(years), 0)

    def test_plot_country_data(self):
        """
        Check if the plot for the Metrics by Country tab is generated correctly.
        """
        chart = self.at.get('plotly_chart')[4]
        self.assertIsNotNone(chart)

    # Testing for Tab 5: Metrics Over Time Graph
    def test_selectbox_both_metric_time(self):
        """
        Check if the primary metric selectbox for the Metrics Over Time tab is working.
        Check if the secondary metric selectbox for the Metrics Over Time tab is working.
        """
        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(
            key="over_time_primary").options, metrics)

        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(
            key="over_time_secondary").options, metrics)

    def test_plot_time_data(self):
        """
        Check if the plot for the Metrics Over Time tab is generated correctly.
        """
        chart = self.at.get('plotly_chart')[5]
        self.assertIsNotNone(chart)

    def test_multiselect_location_metric_time(self):
        """
        Check the multiselect for selecting locations in the Metrics Over Time tab.
        """
        locations = sorted(self.at.multiselect(key="over_time_loc").options)
        self.assertGreater(len(locations), 0)

    # Testing for Tab 6: Country Overview
    def test_selectbox_country_oview_and_spideryr(self):
        """
        Check if the selectbox for selecting a country in the Country Overview tab is populated 
        correctly.
        Check if the selectbox for selecting a year in the Country Overview tab is populated 
        correctly.
        """
        countries = sorted(self.at.selectbox(key="country_country").options)
        self.assertGreater(len(countries), 0)

        years = sorted(self.at.selectbox(key="spider_year").options)
        self.assertGreater(len(years), 0)

    def test_plot_country_overview(self):
        """
        Check if the Country Overview plot is generated correctly.
        """
        chart = self.at.get('plotly_chart')[6]
        self.assertIsNotNone(chart)


if __name__ == '__main__':
    unittest.main()
