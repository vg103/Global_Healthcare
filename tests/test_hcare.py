"""
This script contains a testing class for UI for the streamlit app in 
hcare.py
"""

import unittest
from streamlit.testing.v1 import AppTest
from json import loads


class HcareTest(unittest.TestCase):
    """
    This class tests UI for hcare.py
    """

    def setUp(self):
        """
        The unittest framework automatically runs this `setUp` function before
        each test. We initialize AppTest for the hcare.py file.
        """

        """
        The following line is ignored by pylint because the unittest function 
        self.at raises Pylint Error: Attribute name "at" doesn't confirm to
        snake_case naming style
        """
        #pylint: disable=no-member
        self.at = AppTest.from_file('../hcare/hcare.py').run()
        print("self.at is type: ", type(self.at))

    def test_title(self):
        """
        Tests the title of the dashboard
        """
        self.assertEqual(self.at.title[0].value, "Global Healthcare")

    #Testing for Tab 1: Global Healthcare Systems - Ranking and Scores
    def test_selectbox_ranking_year_home(self):
        """
        Check if the years for ranking list in the home tab are populated
        correctly
        """
        years = sorted(self.at.selectbox(key="home_year").options)
        self.assertGreater(len(years), 0)

    def test_selectbox_metric_home(self):
        """
        Check if the metric selectbox for compscore over time graph is working
        """
        metrics = ["comp_score", "rank"]
        self.assertEqual(self.at.selectbox(key="home_metric").options, metrics)

    def test_multiselect_location_ihme(self):
        """
        Check the multiselect for selecting locations in compscore over time
        graph on the home tab
        """
        locations = sorted(self.at.multiselect(key="home_loc").options)
        self.assertGreater(len(locations), 0)

    def test_plot_compscores_home(self):
        """
        Check if the compscores plot is generated correctly in home tab
        """
        chart = self.at.get('plotly_chart')[0]
        self.assertIsNotNone(chart)

    def test_multiselect_location_ihme(self):
        """
        Check the multiselect for selecting locations in death vs doc graph on
        the home tab
        """
        locations = sorted(self.at.multiselect(key="country1").options)
        self.assertGreater(len(locations), 0)

    def test_plot_compscores_home(self):
        """
        Check if the death vs doc plot is generated correctly in home tab
        """
        chart = self.at.get('plotly_chart')[1]
        self.assertIsNotNone(chart)

    #Testing for Tab 2: IHME Data Graph
    def test_selectbox_metric_ihme(self):
        """
        Check the selectbox for the metric choice in IHME Data tab
        """
        self.assertEqual(self.at.selectbox(key="ihme_measure").options, ["deaths", "incidence"])

    def test_selectbox_year_ihme(self):
        """
        Check if the years for IHME data are populated correctly
        """
        years = sorted(self.at.selectbox(key="ihme_year").options)
        self.assertGreater(len(years), 0)

    def test_multiselect_location_ihme(self):
        """
        Check the multiselect for selecting locations in IHME Data tab
        """
        locations = sorted(self.at.multiselect(key="ihme_loc").options)
        self.assertGreater(len(locations), 0)

    def test_multiselect_cause_ihme(self):
        """
        Check the multiselect for selecting cause in IHME Data tab
        """
        causes = sorted(self.at.multiselect(key="ihm_cause").options)
        self.assertGreater(len(causes), 0)

    def test_multiselect_sex_ihme(self):
        """
        Check the multiselect for selecting sex in IHME Data tab
        """
        sexes = sorted(self.at.multiselect(key="ihm_sex").options)
        self.assertGreater(len(sexes), 0)

    def test_plot_ihme_data(self):
        """
        Check if the plot is generated correctly in IHME Data tab
        """
        chart = self.at.get('plotly_chart')[2]
        self.assertIsNotNone(chart)

    #Testing for Tab 3: WHO Data Graph
    def test_selectbox_year_who(self):
        """
        Check if the years for WHO data are populated correctly
        """
        print(type(self.at.selectbox))
        years_who = sorted(self.at.selectbox(key="who_year").options)
        self.assertGreater(len(years_who), 0)

    def test_multiselect_location_who(self):
        """
        Check the multiselect for selecting locations in WHO Data tab
        """
        locations = sorted(self.at.multiselect(key="who_loc").options)
        self.assertGreater(len(locations), 0)

    def test_plot_who_data(self):
        """
        Check if the plot is generated correctly in WHO Data tab"
        """
        chart = self.at.get('plotly_chart')[3]
        self.assertIsNotNone(chart)

    #Testing for Tab 4: Metrics By Country Graph
    def test_selectbox_primary_metric_country(self):
        """
        Check if the primary metric selectbox for Metrics by Country tab is 
        working
        """
        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(key="country_met_one").options, metrics)

    def test_selectbox_secondary_metric_country(self):
        """
        Check if the secondary metric selectbox for Metrics by Country tab is
        working
        """
        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(key="country_met_two").options, metrics)

    def test_selectbox_year_metric_country(self):
        """
        Check if the years for Metric by Country tab are populated correctly
        """
        years = sorted(self.at.selectbox(key="country_year").options)
        self.assertGreater(len(years), 0)

    def test_multiselect_location_metric_country(self):
        """
        Check the multiselect for selecting locations in metrics by country tab
        """
        locations = sorted(self.at.multiselect(key="country_loc").options)
        self.assertGreater(len(locations), 0)

    def test_plot_country_data(self):
        """
        Check if the plot for Metrics by Country tab is generated correctly
        """
        chart = self.at.get('plotly_chart')[4]
        self.assertIsNotNone(chart)

    #Testing for Tab 5: Metrics Over Time Graph
    def test_selectbox_primary_metric_time(self):
        """
        Check if the primary metric selectbox for Metrics Over Time tab is
        working
        """
        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(key="over_time_primary").options, metrics)

    def test_selectbox_secondary_metric_time(self):
        """
        Check if the secondary metric selectbox for Metrics Over Time tab is
        working
        """
        metrics = ["medical_doctors_per_10000", "nurses_midwifes_per_10000",
                   "pharmacists_per_10000", "dentists_per_10000"]
        self.assertEqual(self.at.selectbox(key="over_time_secondary").options, metrics)

    def test_plot_time_data(self):
        """
        Check if the plot for Metrics Over Time tab is generated correctly"
        """
        chart = self.at.get('plotly_chart')[5]
        self.assertIsNotNone(chart)

    def test_multiselect_location_metric_time(self):
        """
        Check the multiselect for selecting locations in Metrics over Time tab
        """
        locations = sorted(self.at.multiselect(key="over_time_loc").options)
        self.assertGreater(len(locations), 0)

    #Testing for Tab 6: Country Overview
    def test_selectbox_year_country_overview(self):
        """
        Check if the years for country overview tab are populated correctly
        """
        print(type(self.at.selectbox))
        countries = sorted(self.at.selectbox(key="country_country").options)
        self.assertGreater(len(countries), 0)

    def test_selectbox_years_country_overview(self):
        """
        Check if the years for country overview tab are populated correctly
        """
        print(type(self.at.selectbox))
        years = sorted(self.at.selectbox(key="spider_year").options)
        self.assertGreater(len(years), 0)

    def test_plot_who_data(self):
        """
        Check if the plot is generated correctly in country overview tab"
        """
        chart = self.at.get('plotly_chart')[6]
        self.assertIsNotNone(chart)

if __name__ == '__main__':
    unittest.main()
