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


def chunk_user_route(detail_of_trip):
    """ This takes the entire length of the route and breaks it up into
        smaller segments for sampling purposes. """

    segment_size = 0.1  # value to break the entire route into 1/10 segments
    distance_along_line = 0.1  # start distance along line at the segment size

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # since I can't get javascript to load, here's a hacky way of loading json
    # that details the route based on the user's point A and point B
    # detail_of_trip = api.directions(
    #                         (40.760350, -73.976209),
    #                         (40.754009, -73.981097),
    #                         mode="walking"
    #                         )[0]
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    # now that I have javascript sending over the json, load json that details
    # the route based on the user's point A and point B

    # -------------- This section is for interpolation/splitting using shapely
    print "length of route, legs", len(detail_of_trip['legs'])
    first = True  # to see if this is the start position for the entire route
    line_points = []  # stores all the points to the route based on dict passed

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

    # Now load those points into a geometry, here shapely's LineString type.
    route_line = LineString(line_points)

    # break up the line into 1/10 segments, iterate. We are ignoring the 0th
    # element as that's the start position and that's already stored

    segmented_points = []  # creating an empty list to store these points

    # hold all the waypoints and other data
    segmented_points.append({'data': {'waypoints': [] }})

    # for our start points that the user defines, geocoded
    segmented_points[0]['data']['start'] = {}
    segmented_points[0]['data']['end'] = {}

    for i in range(1, 11):
        # Note: the output of interpolate is a Point data type
        # Return a point at the specified distance along a linear geometric object.
        point = route_line.interpolate(distance_along_line, normalized=True)
        print "Point ", i, point

        # call the function that checks to see what geohash the line falls under
        # and if it is a high crime area
        geohash_data = get_position_geohash(point.x, point.y)
        geohash_data['lat'] = point.x
        geohash_data['lng'] = point.y

        if geohash_data['crime_index'] > 0.2:
            # this is a dummy test, but let's assume this is high crime
            # and do something about it
            # do some waypoint stuff here
            # for waypoints ideas: Now that we know that the area is high crime
            # check how far the previous step is from the next step in the
            # dictionary, and then if both steps have a short delta in the same
            # direction, that means to go one grid up-down, or left-right
            # based on that delta value.
            # Ex: check one geohash up and one geohash down, see which one has
            # the lowest crime value out of the 3 points, and go there.
            geohash_data['is_high_crime'] = True
            segmented_points[0]['data']['waypoints'].append({
                'location': {'lat': 40.757560, 'lng': -73.968781},
                'stopover': False  # it's not a stop on the route, but a recalc
                })
        else:
            geohash_data['is_high_crime'] = False

        # extract the datapoints from the point datatype
        segmented_points.append(geohash_data)  # append data on location
        distance_along_line += segment_size

    # also add the point A, point B latitude and longitude that the user gives
    # to the data that will be sent back to JS
    segmented_points[0]['data']['start'] = {
        'lat': line_points[0][0],
        'lng': line_points[0][1]
        }

    segmented_points[0]['data']['end'] = {
        'lat': line_points[-1][0],
        'lng': line_points[-1][1]
        }

    print "segmented_points", json.dumps(segmented_points, indent=2)
    print "\n\n\n\n"  # compensating for the giant GET request

    # return only the waypoints and start/end lat,lngs
    return segmented_points[0]


def get_position_geohash(point_lat, point_lng):
    """ This takes a point and with that point find out what geohash it falls
        under. With that information we could get the crime_index and total_crimes
    """
    # get the lat, lng position and get the geohash and crime_index from the db


    # some raw sql to do the geohash conversion
    geohash_sql = "SELECT * " + \
                  "FROM nyc_crimes_by_geohash " + \
                  "WHERE geohash=" + \
                  "ST_GeoHash(st_makepoint(%s, %s), 7);" % \
                  (point_lat, point_lng)

    # execute the raw sql, and there should only be one result... so get that.
    geohash_query =db.engine.execute(geohash_sql).fetchone()

    geohash_query_data = {
        'geohash': geohash_query[1],
        'total_crimes': geohash_query[2],
        'crime_index': float(geohash_query[3])
        }

    # TODO: Write something that checks queries based on the crime_count desc
    # find the 5th item in that query and say that any geohash with a crime
    # index greater than or equal to the 5th item is considered dangerous

    return geohash_query_data


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
