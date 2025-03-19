from streamlit.testing.v1 import AppTest
import sys
import os
import unittest

# Ensure the hcare directory is in sys.path so that "data_prep" can be found.
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, "../hcare"))


class TestHcareApp(unittest.TestCase):
    def setUp(self):
        """
        Set up the AppTest instance before each test.
        The file is launched via AppTest.from_file(...).run()
        """
        # Launch the app; the default_timeout ensures widgets have time to render.
        self.at = AppTest.from_file("hcare/hcare.py", default_timeout=30).run()

    def test_title(self):
        """
        Test that the app title is rendered correctly.
        In hcare/hcare.py, the title is set with st.title("Global Healthcare").
        """
        # Check that at least one title widget is available.
        self.assertTrue(len(self.at.title) > 0, "No title widget found.")
        self.assertEqual(self.at.title[0].value, "Global Healthcare")

    def test_home_header(self):
        """
        Test that the Home tab contains the expected header.
        For example, the Home tab starts with a header: "Ranking and Scores".
        """
        self.assertTrue(len(self.at.header) > 0, "No header widget found.")
        # Check that the first header matches the expected value.
        self.assertEqual(self.at.header[0].value, "Ranking and Scores")

    def test_home_welcome_text(self):
        """
        Test that the Home tab includes a welcome message.
        The app writes a welcome message with st.write() in the Home tab.
        """
        # Verify that at least one text element exists.
        self.assertTrue(len(self.at.text) > 0, "No text widget found.")
        # Look for a piece of the welcome message in one of the text widgets.
        welcome_found = any(
            "Welcome! This site provides an interactive overview" in text_elem.value
            for text_elem in self.at.text
        )
        self.assertTrue(
            welcome_found, "Welcome message not found in text elements.")


if __name__ == "__main__":
    unittest.main()
