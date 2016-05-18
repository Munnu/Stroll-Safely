import json, requests
from model import Crime_Data_NYC, connect_to_db, db, init_app
#from application import app
from gmaps import Directions, Geocoding

init_app()

api = Directions()
geocoding = Geocoding(sensor=False)

# start and end coordinates in directions
# reminder: results returns a list
results = api.directions((40.728783, -73.7897503),
                         (40.6497484, -73.97767999999999))
# pretty formatting on json, it's great
# print json.dumps(results, indent=2)


def address_to_lat_lng(user_points):
    """ Generates a dictionary of the user's latitude and
        longitude based on address passed into json """

    user_coords = {}

    # get the start and end address from the parameter
    point_a = user_points['start']
    point_b = user_points['end']

    # geocoding magic to convert address to a bunch of properties
    point_a_geo_results = geocoding.geocode(point_a)[0]
    point_b_geo_results = geocoding.geocode(point_b)[0]

    # extract out the latitude and longitude of the geocoding dict results
    # format is {'point_a': {'lat': ..., 'lng': ...}, 'point_b': {...}}
    user_coords['point_a'] = point_a_geo_results['geometry']['location']
    user_coords['point_b'] = point_b_geo_results['geometry']['location']

    return user_coords


def generate_bounds():
    """ draws the bounds for safety analysis around what will be the
        user defined route """

    user_coords = {
                      "point_a": {"lat": 40.760385, "lng": -73.9766736},
                      "point_b": {"lat": 40.7539472, "lng": -73.9811953}
                    }

    if user_coords:
        # takes in user_coords point a and point b
        # in order to determine top left and bottom right coordinates.
        point_a = user_coords['point_a']
        point_b = user_coords['point_b']

        # compare latitude to see what's the top coord, tupleize

        top_left_coord = (max(point_a['lat'], point_b['lat']),
                          min(point_a['lng'], point_b['lng']))
        bottom_right_coord = (min(point_a['lat'], point_b['lat']),
                              max(point_a['lng'], point_b['lng']))

        print top_left_coord, bottom_right_coord


def get_twenty():
    """ Test to see if I could get a list of 20 items from db """

    twenty_entries = Crime_Data_NYC.query.limit(20).all()

    crimes_coords = {'crimes': []}

    print "\n\n\nAAAAAAAAAAAAAAAAAA!!!!!", twenty_entries[0], "\n\n\n\n\n"
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
