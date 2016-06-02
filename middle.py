# ------------------------------------------------------------------------------
# This file holds all of the code that interacts with flask.
# For instance, it does the geocoding part (address_to_lat_lng)
# It dynamically generates the bounds based on the user's start and end location
# Gets the crime records
# ------------------------------------------------------------------------------
import json, requests
from math import cos, sin, radians
from model import Crime_Data_NYC, NYC_Crimes_by_Geohash
from model import connect_to_db, db, init_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
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

    bounds = total_crimes_in_bounds(user_coords)
    return user_coords


def inspect_waypoints(current_point, direction):
    """ inspects to see if this is point is a potential waypoint by taking
    a single point, a distance (constant), and a direction """

    # check if longwise, latwise, all for direction. direction should be a str
    # direction will indicate bearing.

    # inspect potential waypoints
    # one degree of latitude is approximately 10^7 / 90 = 111,111 meters.
    # http://stackoverflow.com/questions/2187657/calculate-second-point-
    # knowing-the-starting-point-and-distance
    # one degree of latitude is approximately 10^7 / 90 = 111,111 meters
    # http://stackoverflow.com/questions/13836416/geohash-and-max-distance
    distance = 118  # meters

    # get the latitude and longitude of the point we will be inspecting
    latitude = current_point[0]
    longitude = current_point[1]

    potential_waypoints = []  # an empty list to store

    if direction == 'latwise' or direction == 'all':
        # then we know our bearing should be 0, 180 for N, S
        east_displacement_n = distance * sin(radians(0)) / 111111
        north_displacement_n = distance * cos(radians(0)) / 111111

        east_displacement_s = distance * sin(radians(180)) / 111111
        north_displacement_s = distance * sin(radians(180)) / 111111

        # calculate the total displacement for N, S respectively
        waypoint_latitude_n = latitude + north_displacement_n
        waypoint_longitude_n = longitude + east_displacement_n

        waypoint_latitude_s = latitude + north_displacement_s
        waypoint_longitude_s = longitude + east_displacement_s

        potential_waypoints.append((waypoint_latitude_n, waypoint_longitude_n))
        potential_waypoints.append((waypoint_latitude_s, waypoint_longitude_s))

    if direction == 'lngwise' or direction == 'all':
        # then we know our bearing should be 90, 270 for E, W
        east_displacement_e = distance * sin(radians(90)) / 111111
        north_displacement_e = distance * cos(radians(90)) / 111111

        east_displacement_w = distance * sin(radians(270)) / 111111
        north_displacement_w = distance * sin(radians(270)) / 111111

        # calculate the total displacement for N, S respectively
        waypoint_latitude_e = latitude + north_displacement_e
        waypoint_longitude_e = longitude + east_displacement_e

        waypoint_latitude_w = latitude + north_displacement_w
        waypoint_longitude_w = longitude + east_displacement_w

        potential_waypoints.append((waypoint_latitude_e, waypoint_longitude_e))
        potential_waypoints.append((waypoint_latitude_w, waypoint_longitude_w))

    # return something like [(late, lnge), (latw, lngw)]
    print "this is potential_waypoints list", potential_waypoints
    return potential_waypoints


def generate_waypoint(lowest_crime_index, points_dict_data, segmented_points):
    """ This function takes in the lowest_crime_index and waypoint dictionary
        to check if the lowest_crime_index is in that waypoint dictionary
        and if so, construct waypoint data to insert into list """

    # passes in something like waypoints_dict_data is [{dictn,}, ... ,{dictw}]
    # points is [(pointn, pointn), ... ,(pointw, pointw)]
    print "inside generate_waypoint"
    print "This is points_dict_data", points_dict_data

    # do a for loop to see if we find the waypoint data that matches
    print "this is points_dict_data", points_dict_data
    for point_data in points_dict_data:
        print "this is point_data", point_data
        if lowest_crime_index in point_data.values():
            print "if statement: lowest_crime_index in point_data"
            # store the waypoint coords
            segmented_points[0]['data']['waypoints'].append({
                'location': {'lat': point_data['point'][0],
                             'lng': point_data['point'][1]},
                'stopover': False  # b/c not stop on the route, a recalc
                })
    # returns nothing, just appends stuff into segmented_points


def try_waypoints():
    """ function that calls all of the other functions repeated in program """
    pass


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
    first = True  # to see if this is the start position for the entire route
    line_points = []  # stores all the points to the route based on dict passed

    for leg in detail_of_trip['legs']:
        for step in leg['steps']:
            # Create a list of two element lists that represent points along the
            # route. via google. line_points = [ [lat1, lng1], [lat2, lng2],...]
            # Only add the starting point the first time. Every other iteration
            # we will just tack on the end points to our line.
            if first:
                line_points.append([step['start_location']['lat'], step['start_location']['lng']])
                first = False
            line_points.append([step['end_location']['lat'], step['end_location']['lng']])

    # Now load those points into a geometry, here shapely's LineString type.
    route_line = LineString(line_points)

# ============ End of get gmap trip legs section
# ---------------------------------------------------------------------------
# ============= Begin Interpolate/Break into 1/10 segments

    # break up the line into 1/10 segments, iterate. We are ignoring the 0th
    # element as that's the start position and that's already stored
    segmented_points = []  # creating an empty list to store these points

    # hold all the waypoints and other data
    segmented_points.append({'data': {'waypoints': []}})

    # for our start points that the user defines, geocoded
    segmented_points[0]['data']['start'] = {}
    segmented_points[0]['data']['end'] = {}

    for i in range(1, 10):  # excluding the start and the end points
        # Note: the output of interpolate is a Point data type
        # Return a point at the specified distance along a linear geometric object.
        point = route_line.interpolate(distance_along_line, normalized=True)
        print "Point ", i, point

        # call the function that checks to see what geohash the line falls under
        # and if it is a high crime area
        # geohash_data is a dict: crime_index, total_crimes, lng, lat, geohash
        geohash_data = get_position_geohash([(point.x, point.y)])[0]  # dict

        # set the is_high_crime variable value to false, for testing
        geohash_data['is_high_crime'] = False

        # extract the datapoints from the point datatype
        geohash_data['lat'] = point.x
        geohash_data['lng'] = point.y

        segmented_points.append(geohash_data)  # append data on location
        distance_along_line += segment_size
        print "crime index:", geohash_data['crime_index'], "geohash:", geohash_data['geohash']

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

# ============ End of Interpolate/Break into 1/10 segments
# ---------------------------------------------------------------------------
# ============= Begin Find bad neighborhood + get geohash center point, look at steps before and after

# def find_crime_areas(segmented_points):
    # once all of the interpolated points are loaded into segmented_points
    # loop through them again to find out which places are high crime.
    bad_neighborhood_crime_index = 0.2
    for j in range(1, len(segmented_points)):
        print "What's goin on?"
        print segmented_points[j]['crime_index'], segmented_points[j]['total_crimes']
        # ====================================================================
        # waypoint algorithm fleshing out
        # ====================================================================
        if segmented_points[j]['crime_index'] > bad_neighborhood_crime_index:
            # get the center of the geohash
            print "This is a bad neighborhood"

            # this is probably temporary, for display purposes
            segmented_points[j]['is_high_crime'] = True

            # some raw sql to get the center coords of geohash
            geohash_center_sql = "SELECT " + \
                "ST_AsText(ST_PointFromGeoHash(geohash)) " + \
                "FROM nyc_crimes_by_geohash " + \
                "WHERE geohash='%s'" % (segmented_points[j]['geohash'])

            # execute the raw sql, and there should only be one result... so get that.
            geohash_center_query = db.engine.execute(geohash_center_sql).fetchone()

            # some string splitting to extract data
            location = geohash_center_query[0].strip("POINT(").rstrip(")").split()
            latitude = location[0]
            longitude = location[1]

            # do a conditional that if the bad neighborhood is at
            # len(segmented_points) we need to go get the end dict

            # now that we know what the bad neighborhood point is, let's get
            # the latitude, longitude from the point before and the point after
            if 'lat' not in segmented_points[j-1] or 'lng' not in segmented_points[j-1]:
                point_before = (segmented_points[j-1]['data']['start']['lat'],
                                segmented_points[j-1]['data']['start']['lng'])
            else:
                point_before = (segmented_points[j-1]['lat'],
                                segmented_points[j-1]['lng'])

            if 'lat' not in segmented_points[j+1] or 'lng' not in segmented_points[j+1]:
                point_after = (segmented_points[j+1]['data']['end']['lat'],
                               segmented_points[j+1]['data']['end']['lng'])
            else:
                point_after = (segmented_points[j+1]['lat'],
                               segmented_points[j+1]['lng'])

            current_point = (segmented_points[j]['lat'],
                             segmented_points[j]['lng'])

            # before calling inspect_waypoints, check the deltas for the
            # step before and the step after to determine whether the function
            # needs to be called twice, or four times, and what direction to go
            # get the change in latitude and longitude between the before
            # and current point location
            delta_lat_before_current = current_point[0] - point_before[0]
            delta_lng_before_current = current_point[1] - point_before[1]

            # get the change in latitude and longitude between the before
            # and current point location
            delta_lat_after_current = point_after[0] - current_point[0]
            delta_lng_after_current = point_after[0] - current_point[1]

# ============= End of Find bad neighborhood + get geohash center point, look at steps before and after
# ---------------------------------------------------------------------------
# ============= Begin check total delta x,y's and what directions to try adding waypoints

            # check to see if the delta x's in both directions are longer
            # than the delta y's in both directions
            if (delta_lat_before_current > delta_lng_before_current) and \
               (delta_lat_after_current > delta_lng_after_current):
                print "inside first if"
                # the latitudes are longer than the longitudes, get waypoints
                # in the longitude direction

                # don't forget to generate waypoints
                waypoint_e_w = inspect_waypoints(current_point, "lngwise")

                # retreive the latitude, longitude coordinates from the ret
                waypoint_e = waypoint_e_w[0]  # a tuple
                waypoint_w = waypoint_e_w[1]  # a tuple

                print "waypoint_data_e", waypoint_e, type(waypoint_e)
                print "waypoint_data_w", waypoint_w, type(waypoint_w)

                # store the waypoints retreived and compare their crime_index
                waypoint_e_w_geohash_data = get_position_geohash(
                    [waypoint_e, waypoint_w])  # ret [{dicte}, {dictw}]

                waypoint_e_geohash_data = waypoint_e_w_geohash_data[0]
                waypoint_w_geohash_data = waypoint_e_w_geohash_data[1]

                waypoint_e_geohash_data['point'] = waypoint_e
                waypoint_w_geohash_data['point'] = waypoint_w

                lowest_crime_index = min(
                    waypoint_e_geohash_data['crime_index'],
                    waypoint_w_geohash_data['crime_index'],
                    segmented_points[j]['crime_index'])

                # check and assemble dict for lowest_crime_index waypoint
                generate_waypoint(lowest_crime_index,
                                  [waypoint_e_geohash_data,
                                   waypoint_w_geohash_data],
                                  segmented_points)

            elif (delta_lng_before_current > delta_lat_before_current) and \
                 (delta_lng_after_current > delta_lat_after_current):
                print "inside elif, checks the north and south creation"
                # the longitudes are longer than the latitudes, get waypoints
                # in the latitude direction

                # don't forget to generate waypoints
                waypoint_n_s = inspect_waypoints(current_point, "latwise")

                # retreive the latitude, longitude coordinates from the ret
                waypoint_n = waypoint_n_s[0]  # a tuple
                waypoint_s = waypoint_n_s[1]  # a tuple

                print "waypoint_n", waypoint_n, type(waypoint_n)
                print "waypoint_s", waypoint_s, type(waypoint_s)

                # store the waypoints retreived and compare their crime_index
                waypoint_n_s_geohash_data = get_position_geohash(
                    [waypoint_n, waypoint_s])  # ret [{dictn}, {dicts}]

                waypoint_n_geohash_data = waypoint_n_s_geohash_data[0]
                waypoint_s_geohash_data = waypoint_n_s_geohash_data[1]

                waypoint_n_geohash_data['point'] = waypoint_n
                waypoint_s_geohash_data['point'] = waypoint_s

                lowest_crime_index = min(
                    waypoint_n_geohash_data['crime_index'],
                    waypoint_s_geohash_data['crime_index'],
                    segmented_points[j]['crime_index'])

                print "waypoint_n_geohash_data['crime_index']", \
                    waypoint_n_geohash_data['crime_index']

                print "waypoint_s_geohash_data['crime_index']", \
                    waypoint_s_geohash_data['crime_index']

                print "segmented_points[j]['crime_index']", \
                    segmented_points[j]['crime_index']

                print "lowest_crime_index", lowest_crime_index

                # check and assemble dict for lowest_crime_index waypoint
                generate_waypoint(lowest_crime_index,
                                  [waypoint_n_geohash_data,
                                   waypoint_s_geohash_data],
                                  segmented_points)
            else:
                print "inside else, checks all directions NS-EW"

                # don't forget to generate waypoints
                waypoint_all = inspect_waypoints(current_point, "all")

                # retreive the latitude, longitude coordinates from the ret
                waypoint_n = waypoint_all[0]
                waypoint_s = waypoint_all[1]

                print "waypoint_n", waypoint_n, type(waypoint_n)
                print "waypoint_s", waypoint_s, type(waypoint_s)

                # retreive the latitude, longitude coordinates from the ret
                waypoint_e = waypoint_all[2]
                waypoint_w = waypoint_all[3]

                print "waypoint_e", waypoint_e, type(waypoint_e)
                print "waypoint_w", waypoint_w, type(waypoint_w)

                # store the waypoints retreived and compare their crime_index
                # ret [{dictn}, ... , {dictw}]
                waypoint_all_geohash_data = get_position_geohash(
                    [waypoint_n, waypoint_s, waypoint_e, waypoint_w])

                waypoint_n_geohash_data = waypoint_all_geohash_data[0]
                waypoint_s_geohash_data = waypoint_all_geohash_data[1]
                waypoint_e_geohash_data = waypoint_all_geohash_data[2]
                waypoint_w_geohash_data = waypoint_all_geohash_data[3]

                waypoint_n_geohash_data['point'] = waypoint_n
                waypoint_s_geohash_data['point'] = waypoint_s

                waypoint_e_geohash_data['point'] = waypoint_e
                waypoint_w_geohash_data['point'] = waypoint_w

                # get the lowest crime index out of the bunch
                lowest_crime_index = min(
                    waypoint_n_geohash_data['crime_index'],
                    waypoint_s_geohash_data['crime_index'],
                    waypoint_e_geohash_data['crime_index'],
                    waypoint_w_geohash_data['crime_index'],
                    segmented_points[j]['crime_index'])

                # check and assemble dict for lowest_crime_index waypoint
                generate_waypoint(lowest_crime_index,
                                  [waypoint_n_geohash_data,
                                   waypoint_s_geohash_data,
                                   waypoint_e_geohash_data,
                                   waypoint_w_geohash_data],
                                  segmented_points)

    # print "segmented_points", json.dumps(segmented_points, indent=2)
    print "\n\n\n\n"  # compensating for the giant GET request

    # return only the waypoints and start/end lat,lngs
    return segmented_points[0]


def get_position_geohash(points):
    """ This takes points and with these points find out what geohash each falls
        under. Then we could get the crime_index and total_crimes
    """

    # takes in a list as a parameter of [(lat, lng) ... (lat, lng)]
    coords_data = []  # to store the dictionary generated

    # do something like a for loop over here
    for point in points:
        geohash_sql = "SELECT * " + \
                      "FROM nyc_crimes_by_geohash " + \
                      "WHERE geohash=" + \
                      "ST_GeoHash(st_makepoint(%s, %s), 7);" % \
                      (point[0], point[1])

        # execute the raw sql, and there should only be one result... so get that.
        geohash_query = db.engine.execute(geohash_sql).fetchone()

        if geohash_query is None:
            # TODO: if the geohash isn't found, need to do something, maybe set it to
            # another geohash type that's low crime...?
            geohash_query = [0, 'hfuf6ge', 0, 0.0]

        geohash_query_data = {
            'geohash': geohash_query[1],
            'total_crimes': geohash_query[2],
            'crime_index': float(geohash_query[3])
            }
        coords_data.append(geohash_query_data)

    # return something like [{dicte}, {dictw}], or {dict}, based on total pts
    return coords_data


def total_crimes_in_bounds(user_coords):
    """ generates the bounds for safety analysis around what will be the
        user defined route. The heatmap data will use this to display crimes.
    """

    crimes_coords = {'crimes': []}

    # takes in user_coords point a and point b
    # in order to determine top left and bottom right coordinates.
    point_a = user_coords['point_a']
    point_b = user_coords['point_b']

    # compare latitude to see what's the top coord, tupleize
    # add 0.005 to latitude, and subtract 0.02 to longitude
    top_left_coord = {'lat': max(point_a['lat'], point_b['lat']) + 0.005,
                      'lng': min(point_a['lng'], point_b['lng']) - 0.02}

    # subtract 0.005 to latitude, and add 0.02 to longitude
    bottom_right_coord = {'lat': min(point_a['lat'], point_b['lat']) - 0.005,
                          'lng': max(point_a['lng'], point_b['lng']) + 0.02}

    # {'lat': 40.765385, 'lng': -74.00119529999999}
    # {'lat': 40.748947199999996, 'lng': -73.9566736}
    print "this is the top_left_coord and bottom_right_coord", \
        top_left_coord, bottom_right_coord

    # once the bounds are generated, we will want to do a query for all of the
    # geohashes that are within those bounds. Let's do that now.
    # some raw sql to get the center coords of geohash
    geohash_in_bounds_sql = "SELECT *, " + \
        "ST_AsText(ST_PointFromGeoHash(geohash)) AS lat_lng " + \
        "FROM nyc_crimes_by_geohash " + \
        "WHERE ST_Contains(" + \
        "ST_MakeBox2D(" + \
        "ST_Point(%f, %f), ST_Point(%f, %f)), ST_PointFromGeoHash(geohash));" \
        % (top_left_coord['lat'], top_left_coord['lng'],
            bottom_right_coord['lat'], bottom_right_coord['lng'])
    # execute the raw sql, there should be many
    geohash_in_bounds_query = db.engine.execute(geohash_in_bounds_sql).fetchall()

    print "This is geohash_in_bounds_query", geohash_in_bounds_query

    for row in geohash_in_bounds_query:
        print "This is row", row
        # strip the lat, lngs before putting them in
        # some string splitting to extract data
        location = row[4].strip("POINT(").rstrip(")").split()
        latitude = location[0]
        longitude = location[1]

        format_loc_dict = {'latitude': latitude, 'longitude': longitude,
                           'total_crimes': row[2]}

        # append to crimes_coords inner list
        crimes_coords['crimes'].append(format_loc_dict)

    return crimes_coords
