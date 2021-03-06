# ------------------------------------------------------------------------------
# This file holds all of the code that interacts with flask.
# For instance, it does the geocoding part (address_to_lat_lng)
# It dynamically generates the bounds based on the user's start and end location
# Gets the crime records
# ------------------------------------------------------------------------------
from math import cos, sin, radians
from model import db, init_app
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


def execute_waypoint_sequence(detail_of_trip):
    """ commence all function calls necessary for waypoint discovery """

    # rets (route_line, line_points)
    sliced_route_and_line_points = chunk_user_route(detail_of_trip)

    sliced_route = sliced_route_and_line_points[0]
    line_points = sliced_route_and_line_points[1]

    # Interpolate/Break into 1/10 segments
    segmented_points = interpolate_points(sliced_route, line_points)
    waypoints = find_crime_areas(segmented_points)

    # print "segmented_points", json.dumps(segmented_points, indent=2)
    print "\n\n\n\n"  # compensating for the giant GET request
    return waypoints


def distance_to_coords_formula(latitude, longitude, bearing1, bearing2):
    """ math formula for calculating the lat, lng based on
        distance and bearing """

    # one degree of latitude is approximately 10^7 / 90 = 111,111 meters.
    # http://stackoverflow.com/questions/2187657/calculate-second-point-
    # knowing-the-starting-point-and-distance
    # one degree of latitude is approximately 10^7 / 90 = 111,111 meters
    # http://stackoverflow.com/questions/13836416/geohash-and-max-distance
    distance = 118  # meters

    east_displacement_a = distance * sin(radians(bearing1)) / 111111
    north_displacement_a = distance * cos(radians(bearing1)) / 111111

    east_displacement_b = distance * sin(radians(bearing2)) / 111111
    north_displacement_b = distance * cos(radians(bearing2)) / 111111

    # calculate the total displacement for N, S respectively
    waypoint_latitude_a = latitude + north_displacement_a
    waypoint_longitude_a = longitude + east_displacement_a

    waypoint_latitude_b = latitude + north_displacement_b
    waypoint_longitude_b = longitude + east_displacement_b

    return [(waypoint_latitude_a, waypoint_longitude_a),
            (waypoint_latitude_b, waypoint_longitude_b)]


def inspect_waypoints(current_point, direction):
    """ inspects to see where is a potential waypoint by taking
    a single point, a distance (constant), and a direction """

    # check if longwise, latwise, all for direction. direction should be a str
    # direction will indicate bearing.

    # get the latitude and longitude of the point we will be inspecting
    latitude = current_point[0]
    longitude = current_point[1]

    potential_waypoints = []  # an empty list to store

    if direction == 'latwise' or direction == 'all':
        # then we know our bearing should be 0, 180 for N, S
        potential_points_found = distance_to_coords_formula(latitude, longitude,
                                                            0, 180)
        potential_waypoints.extend(potential_points_found)

    if direction == 'lngwise' or direction == 'all':
        # then we know our bearing should be 90, 270 for E, W
        potential_points_found = distance_to_coords_formula(latitude, longitude,
                                                            90, 270)
        potential_waypoints.extend(potential_points_found)

    # return something like [(late, lnge), (latw, lngw)]
    return potential_waypoints


def try_waypoints(waypoint_data, current_point, segmented_points):
    """ function that calls all of the other functions repeated in program """

    # waypoint_data will be a list [waypoint_n, ... , waypoint_w]
    # where waypoint_n ... w is (lat, lng)

    # store the waypoints retreived and compare their crime_index
    # ret [{dicte}, {dictw}]
    waypoint_geohash_data_all = get_position_geohash(waypoint_data)
    crime_index_storage = []
    for data in waypoint_geohash_data_all:
        crime_index_storage.append(data['crime_index'])
    crime_index_storage.append(current_point['crime_index'])

    lowest_crime_index = min(*crime_index_storage)

    # check and assemble dict for lowest_crime_index waypoint
    generate_waypoint(lowest_crime_index,
                      waypoint_geohash_data_all,
                      segmented_points)


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
            # store the waypoint coords
            segmented_points[0]['data']['waypoints'].append({
                'location': {'lat': point_data['point'][0],
                             'lng': point_data['point'][1]},
                'stopover': False  # b/c not stop on the route, a recalc
            })
    # returns nothing, just appends stuff into segmented_points


def chunk_user_route(detail_of_trip):
    """ This takes the entire length of the route and breaks it up into
        smaller segments for sampling purposes. """

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
    return (route_line, line_points)


# ============ End of get gmap trip legs section
# ---------------------------------------------------------------------------
# ============= Begin Interpolate/Break into 1/10 segments
def interpolate_points(route_line, line_points):
    """ Interpolate/Break into 1/10 segments """

    segment_size = 0.1  # value to break the entire route into 1/10 segments
    distance_along_line = 0.1  # start distance along line at the segment size

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

    return segmented_points


# ============ End of Interpolate/Break into 1/10 segments
# ---------------------------------------------------------------------------
# ============= Begin Find bad neighborhood + get geohash center point
# look at steps before and after
def find_crime_areas(segmented_points):
    """ Find bad neighborhood + get geohash center point,
        look at steps before and after """

    # once all of the interpolated points are loaded into segmented_points
    # loop through them again to find out which places are high crime.
    bad_neighborhood_crime_index = 0.2

    for j in range(1, len(segmented_points)):
        print "segmented_points[j]", segmented_points[j]
        # ====================================================================
        # waypoint algorithm fleshing out
        # ====================================================================
        if segmented_points[j]['crime_index'] > bad_neighborhood_crime_index:
            # get the center of the geohash
            print "This is a bad neighborhood"

            # this is probably temporary, for display purposes
            segmented_points[j]['is_high_crime'] = True

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
            delta_lng_after_current = point_after[1] - current_point[1]

            delta_before_after = [delta_lat_before_current, delta_lng_before_current,
                                  delta_lat_after_current, delta_lng_after_current]

            segmented_points = check_directions_find_waypoint(current_point,
                                                              segmented_points[j],
                                                              delta_before_after,
                                                              segmented_points)
    print "this is segmented_points[0] returned", segmented_points[0]
    return segmented_points[0]


# ============= End of Find bad neighborhood + get geohash center point
#  look at steps before and after
# ---------------------------------------------------------------------------
# ============= Begin check total delta x,y's and what directions
# to try adding waypoints
def check_directions_find_waypoint(current_point, current_segment,
                                   delta_before_after, segmented_points):
    """ check total delta x,y's and what directions to try adding waypoints """

    delta_lat_before_current = delta_before_after[0]
    delta_lng_before_current = delta_before_after[1]

    delta_lat_after_current = delta_before_after[2]
    delta_lng_after_current = delta_before_after[3]

    # check to see if the delta x's in both directions are longer
    # than the delta y's in both directions
    if (delta_lat_before_current > delta_lng_before_current) and \
       (delta_lat_after_current > delta_lng_after_current):
        print "inside first if"
        # the latitudes are longer than the longitudes, get waypoints
        # in the longitude direction

        # don't forget to generate waypoints
        waypoint_e_w = inspect_waypoints(current_point, "lngwise")
        try_waypoints(waypoint_e_w, current_segment, segmented_points)
    elif (delta_lng_before_current > delta_lat_before_current) and \
         (delta_lng_after_current > delta_lat_after_current):
        print "inside elif, checks the north and south creation"
        # the longitudes are longer than the latitudes, get waypoints
        # in the latitude direction

        # don't forget to generate waypoints
        waypoint_n_s = inspect_waypoints(current_point, "latwise")
        try_waypoints(waypoint_n_s, current_segment, segmented_points)
    else:
        print "inside else, checks all directions NS-EW"

        # don't forget to generate waypoints
        waypoint_all = inspect_waypoints(current_point, "all")
        try_waypoints(waypoint_all, current_segment, segmented_points)

    # return only the waypoints and start/end lat,lngs
    return segmented_points


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
            # if the geohash isn't found, need to do something,
            # query PostGIS for the geohash (not in db)
            # then assume that there are no crimes in the area
            geohash_of_point = "SELECT ST_GeoHash(geometry(Point(%s, %s)), 7);" \
                % (point[0], point[1])

            geohash_found = db.engine.execute(geohash_of_point).fetchone()

            geohash_query = [0, geohash_found[0], 0, 0.0]

        geohash_query_data = {
            'geohash': geohash_query[1],
            'total_crimes': geohash_query[2],
            'crime_index': float(geohash_query[3]),
            'point': point
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

    for row in geohash_in_bounds_query:
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
