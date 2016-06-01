from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from geoalchemy2.types import Geometry

# instantiates a SQLAlchemy type
db = SQLAlchemy()


class NYC_Crimes_by_Geohash(db.Model):
    """ Table that holds the geohash data and the total number of crimes
        per geohash and the crime index based on that geohash """

    __tablename__ = "nyc_crimes_by_geohash"

    # I really shouldn't have an id, my geohash can be my id.
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    geohash = db.Column(db.String)
    total_crimes = db.Column(db.Integer)
    crime_index = db.Column(db.Float)

    # define relationship to NYC_Crimes_by_Geohash
    crime_data_nyc = db.relationship('Crime_Data_NYC',
                                     backref=db.backref("nyc_crimes_by_geohash"))


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
    # location = db.Column(db.String)
    location = db.Column(Geometry(geometry_type='POINT'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    geohash = db.Column(db.String, db.ForeignKey(NYC_Crimes_by_Geohash.geohash))


####################################################
# Helper functions
####################################################
def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app, db_uri='postgres:///crime_data_gis'):
    """Connect the database to our Flask app."""

    # Configure to use our database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    # app.config['SQLALCHEMY_ECHO'] = True
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
