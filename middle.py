import json
from model import Crime_Data_NYC, connect_to_db, db
from application import app
from gmaps import Directions

api = Directions()

# start and end coordinates in directions
# reminder: results returns a list
results = api.directions((40.728783, -73.7897503),
                         (40.6497484, -73.97767999999999))

# print json.dumps(results, indent=2)

def get_twenty():
    """ Test to see if I could get a list of 20 items from db """
    twenty_entries = Crime_Data_NYC.query.filter_by(crime_id=26818).first()
    print "This is twenty entries", twenty_entries



if __name__ == '__main__':
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    connect_to_db(app)
    get_twenty()
