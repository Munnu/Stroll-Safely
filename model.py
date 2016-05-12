#from flask.ext.sqlalchemy import SQLAlchemy
from geoalchemy2.types import Geometry

# instantiates a SQLAlchemy type
db = SQLAlchemy()

class Crime_Data_NYC(db.Model):
    """ Crime data from NYC Open Data """

    __tablename__ = "crime_data_nyc"

    crime_id = db.Column(db.Integer, autoincrement=True, primary_key=True) 
    occurrence_date = db.Column(db.DateTime)
    day_of_week = db.Column(db.String)
    occurrence_month = db.Column(db.Integer)
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
    location = db.Column(Geometry(geometry_type='POINT', srid=4326))

####################################################
# Helper functions
####################################################

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///crime_data'
    app.config['SQLALCHEMY_ECHO'] = False       # Set to False to hide verbose output
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    db.create_all()
