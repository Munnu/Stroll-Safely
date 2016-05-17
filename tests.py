import os
from unittest import TestCase
# from model import Employee, Department, connect_to_db, db, example_data
from model import Crime_Data_NYC, connect_to_db, db, create_engine
from application import app
import application


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
        connect_to_db(app, "postgresql:///test_data")

    def test_homepage(self):
        """ hit up that root endpoint """

        result = self.client.get("/")
        self.assertIn("Route Me", result.data)

    def test_crimes_json(self):
        """ hit up that crimes json from the get_twenty
            to see if it renders properly """

        result = self.client.get("/crimes.json")
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
        connect_to_db(app, "postgresql:///test_data")
        #conn = db.create_engine('postgres:///test_data').raw_connection()

        # # Create tables and add sample data
        # db.create_all()  # for table creation, based off the class in model.py
        # db.session.commit()

        # Test_Crimes.query.delete()  # for data loading that's ran more than once

        # # data loading section from csv
        # csv_file_path = os.path.dirname(os.path.abspath(__file__)) + \
        #     '/csv_files/unit_test_crime_data.csv'

        # with open(csv_file_path, 'r') as f:
        #     sql = "COPY test_crimes FROM '%s' WITH CSV HEADER DELIMITER AS ','" % csv_file_path
        #     result = db.engine.execute(sql)
        #     db.session.commit()

    # def tearDown(self):
    #     """Do at end of every test."""

    #     db.session.close()
    #     db.drop_all()

    def test_assert(self):
        """ dummy test to see if things work, allows loading of
            data into db if setup creates new table with data """

        self.assertTrue(True)

    def test_get_a_crime(self):
        """Can we retreive a crime in the sample data?"""

        crime = Crime_Data_NYC.query.limit(1).first()
        self.assertTrue(crime)


# class MockFlaskTests(TestCase):
#     """Flask tests that show off mocking."""

#     def setUp(self):
#         """Stuff to do before every test."""

#         # Get the Flask test client
#         self.client = app.test_client()

#         # Show Flask errors that happen during tests
#         app.config['TESTING'] = True

#         # Connect to test database
#         connect_to_db(app, "postgresql:///testdb")

#         # Create tables and add sample data
#         db.create_all()
#         example_data()

#         # Make mock
#         def _mock_state_to_code(state_name):
#             return "CA"

#         server.state_to_code = _mock_state_to_code

#     def tearDown(self):
#         """Do at end of every test."""

#         db.session.close()
#         db.drop_all()

#     def test_emps_by_state_with_mock(self):
#         """Find employees in a state."""

#         result = self.client.post("/emps-by-state", data={'state':'California'})
#         self.assertIn("Nadine", result.data)


if __name__ == "__main__":
    import unittest

    unittest.main()
