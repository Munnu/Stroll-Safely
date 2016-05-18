from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from geoalchemy2.types import Geometry

# instantiates a SQLAlchemy type
db = SQLAlchemy()


class Crime_Data_NYC(db.Model):
    """ Crime data from NYC Open Data """

    __tablename__ = "crime_data_nyc"

    crime_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    occurrence_date = db.Column(db.DateTime)
    day_of_week = db.Column(db.String)
    occurrence_month = db.Column(db.String)
    occurrence_day = db.Column(db.Integer)
    occurrence_year = db.Column(db.Integer)
    occurrence_hour = db.Column(db.Integer)
    compstat_month = db.Column(db.Integer)
    compstat_day = db.Column(db.Integer)
    compstat_year = db.Column(db.Integer)
    offense = db.Column(db.String)
    offense_classification = db.Column(db.String)
    sector = db.Column(db.String)
    precinct = db.Column(db.Integer)
    borough = db.Column(db.String)
    jurisdiction = db.Column(db.String)
    xcoordinate = db.Column(db.Integer)
    ycoordinate = db.Column(db.Integer)
    location = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    # location = db.Column(Geometry(geometry_type='POINT'))
    # location = db.Column(db.Integer)
    # location = db.Column(Geometry(geometry_type='POINT', srid=4326))


####################################################
# Helper functions
####################################################


def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app, db_uri='postgres:///crime_data'):
    """Connect the database to our Flask app."""

    # Configure to use our database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
