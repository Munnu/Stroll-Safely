# ------------------------------------------------------------------------------
# This file holds all of the code that interacts with flask.
# For instance, it does the geocoding part (address_to_lat_lng)
# It dynamically generates the bounds based on the user's start and end location
# Gets the crime records
# ------------------------------------------------------------------------------
import json, requests
from model import Crime_Data_NYC, NYC_Crimes_by_Geohash
from model import connect_to_db, db, init_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
#from application import app  # causes circular reference, nevermind
from gmaps import Directions, Geocoding
from shapely.geometry import LineString


init_app()

api = Directions()
geocoding = Geocoding(sensor=False)

# start and end coordinates in directions
# reminder: results returns a list
# results = api.directions((40.728783, -73.7897503),
#                          (40.6497484, -73.97767999999999))
# # pretty formatting on json, it's great
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


def get_route_dict(detail_of_trip):
    """ I haven't thought of a better name yet, I'll figure it out as I type """

    # why does this not work?
    # print "!!!!!!!!!!!!!!!"
    # detail_of_trip = json.loads(detail_of_trip)
    detail_of_trip = dict(detail_of_trip)

    # print "\n\n\n\n\n!!!!!!!!!!", detail_of_trip

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # since I can't get javascript to load, here's a hacky way of loading json
    # that details the route based on the user's point A and point B
    # detail_of_trip = api.directions(
    #                         (user_coords['point_a']['lat'], 
    #                         user_coords['point_a']['lng']),
    #                         (user_coords['point_b']['lat'], 
    #                         user_coords['point_b']['lng']),
    #                         mode="walking"
    #                         )

    # detail_of_trip = api.directions(
    #                         (40.760350, -73.976209),
    #                         (40.754009, -73.981097),
    #                         mode="walking"
    #                         )[0]

    print "==========================================="
    print type(detail_of_trip)
    print "==========================================="
    # # print json.dumps(detail_of_trip['legs'], indent=2)
    # print json.dumps(detail_of_trip, indent=2)
    # print type(detail_of_trip)
    # print "==========================================="
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    # now that I have javascript sending over the json, load json that details
    # the route based on the user's point A and point B


    # -------------- This section is for interpolation/splitting using shapely
    print "length of route, legs", len(detail_of_trip['legs'])
    print "\n\n\n\n"  # compensating for the giant GET request
    first = True
    line_points = []
    for leg in detail_of_trip['legs']:
        for step in leg['steps']:
            # Create a list of two element lists that represent points along the
            # route. line_points = [ [lat1, lng1], [lat2, lng2], ... ]
            # Only add the starting point the first time. Every other iteration
            # we will just tack on the end points to our line.
            if first:
                line_points.append([step['start_location']['lat'], step['start_location']['lng']])
                first = False
            line_points.append([step['end_location']['lat'], step['end_location']['lng']])
    print "This is line_points", line_points

    return "get_route_dict"


def get_position_geohash(detail_of_trip):
    """ This takes a point and with that point find out what geohash it falls
        under. With that information we could get the crime_index and total_crimes
    """
    # a test to see if I could get the latlng of the first step's start pos
    # and get the geohash and crime_index from the database
    first_step_start_loc = detail_of_trip['legs'][0]['steps'][0]['start_location']
    print json.dumps(first_step_start_loc, indent=2)

    # some raw sql to do the geohash conversion
    geohash_sql = "SELECT * " + \
                  "FROM nyc_crimes_by_geohash " + \
                  "WHERE geohash=" + \
                  "ST_GeoHash(st_makepoint(%s, %s), 7);" % \
                  (first_step_start_loc['lat'], first_step_start_loc['lng'])

    # execute the raw sql
    geohash_query =db.engine.execute(geohash_sql)

    # there should be only one result, so
    geohashes_found = ()
    for row in geohash_query:
        geohashes_found = row[1:]

    # TODO: Write something that checks queries based on the crime_count desc
    # find the 5th item in that query and say that any geohash with a crime
    # index greater than or equal to the 5th item is considered dangerous

    print "************************************"
    print geohashes_found  # format is (geohash, total_crimes, crime_index)
    print type(geohashes_found[-1])  # is of decimal.decimal type, that's okay
    print "************************************"

    return "get_position_geohash"


def get_twenty():
    """ Test to see if I could get a list of 20 items from db """

    twenty_entries = Crime_Data_NYC.query.limit(20).all()

    crimes_coords = {'crimes': []}

    # print "\n\n\nAAAAAAAAAAAAAAAAAA!!!!!", twenty_entries[0], "\n\n\n\n\n"
    for entry in twenty_entries:
        # get the location in string format of "(0, 0)"
        # and other nasty string to float conversion stuff here
        location_lat = entry.latitude
        location_lng = entry.longitude

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
