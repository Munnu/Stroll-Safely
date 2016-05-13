import json
from model import Crime_Data_NYC, connect_to_db, db, init_app
#from application import app
from gmaps import Directions

init_app()

api = Directions()

# start and end coordinates in directions
# reminder: results returns a list
results = api.directions((40.728783, -73.7897503),
                         (40.6497484, -73.97767999999999))

# print json.dumps(results, indent=2)


def get_twenty():
    """ Test to see if I could get a list of 20 items from db """

    twenty_entries = Crime_Data_NYC.query.limit(20).all()

    crimes_coords = {'crimes': []}

    for entry in twenty_entries:
        # get the location in string format of "(0, 0)"
        # and other nasty string to float conversion stuff here
        location = entry.location[1:-1].split(",")
        location_lat = float(location[0].strip())
        location_lng = float(location[1].strip())

        format_loc_dict = {'latitude': location_lat, 'longitude': location_lng}

        # append to crimes_coords inner list
        crimes_coords['crimes'].append(format_loc_dict)

    return crimes_coords


# if __name__ == "__main__":
#     connect_to_db(app)

#     # In case tables haven't been created, create them
#     db.create_all()

#     # Import different types of data
#     get_twenty()
