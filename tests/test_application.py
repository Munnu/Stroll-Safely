from unittest import TestCase
from model import Crime_Data_NYC
from model import connect_to_db
from application import app

class FlaskTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        # party like a rockstar, totally dude.
        print 'SETUP for Flask'

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        # connect_to_db(app, "postgresql:///test_data")  # not using this now
        connect_to_db(app, "postgres:///crime_data_gis")

    def test_homepage(self):
        """ hit up that root endpoint """

        result = self.client.get("/")
        self.assertIn("Route Me", result.data)

    def test_crimes_json(self):
        """ hit up that crimes json to see if it renders properly """

        start_lat = "40.7484405"
        start_lng = "-73.98566439999999"
        end_lat = "40.7505423"
        end_lng = "-73.9877176"

        result = self.client.get("/crimes.json?start_lat=" + start_lat +
                                 "&start_lng=" + start_lng + "&end_lat=" + end_lat +
                                 "&end_lng=" + end_lng)
        self.assertIn("latitude", result.data)

    def test_start_end_json(self):
        """ If possible, force in a start and end point and get that json """

        result = self.client.get("/start-end.json?start=666 Fifth Avenue" +
                                 "New York NY 10019&end=11 W 53rd St New York NY 10019")
        self.assertIn('"lat": 40.7603833', result.data)


class DatabaseTests(TestCase):
    def setUp(self):
        """Stuff to do before every test."""

        # party like a rockstar, totally dude.
        print 'SETUP for Database!'

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        # connect_to_db(app, "postgresql:///test_data")  # not using this
        connect_to_db(app, "postgresql:///crime_data_gis")

    def test_assert(self):
        """ dummy test to see if things work, allows loading of
            data into db if setup creates new table with data """

        self.assertTrue(True)

    def test_get_a_crime(self):
        """Can we retreive a crime in the sample data?"""

        crime = Crime_Data_NYC.query.limit(1).first()
        self.assertTrue(crime)

if __name__ == "__main__":
    import unittest

    unittest.main()
