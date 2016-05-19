# ------------------------------------------------------------------------------
# This file holds all of the code that interacts with flask.
# For instance, it does the geocoding part (address_to_lat_lng)
# It dynamically generates the bounds based on the user's start and end location
# Gets the crime records
# ------------------------------------------------------------------------------
import json, requests
from model import Crime_Data_NYC, connect_to_db, db, init_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
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

    # new edition! We will also add in the inner bounds that the route will encompass
    # first we need to find out which corners are our top left and bottom right
    # call generate_bounds, this does the trick
    inner_boundary_coords = generate_bounds(user_coords)  # returns a tuple
    print "\n\n\n\n THIS IS INNER_BOUNDARY_COORDS", inner_boundary_coords
    user_coords['top_left_inner_bound'] = inner_boundary_coords[0]
    user_coords['bottom_right_inner_bound'] = inner_boundary_coords[1]

    # Let's see how generate_crime_grid loads
    generate_crime_grid(user_coords)

    return user_coords


def generate_crime_grid(user_coords):
    """ This takes the bounds based on the user's route and
        generates the crime (relative location) crime grid """

    crime_array = []  # initalize an empty (2d) array
    crime_totals = []  # this holds the total number of crimes found in each grid

    chunk_number = 4  # just an arbitrary number to break up grid

    # end_x - start_x, divided by arbitary number to break up grid into N slots
    offset_x = ( user_coords['bottom_right_inner_bound']['lng']
                 - user_coords['top_left_inner_bound']['lng'] ) / chunk_number

    # end_y - start_y, divided by arbitrary number to break up grid into N slots
    offset_y = ( user_coords['bottom_right_inner_bound']['lat']
                 - user_coords['top_left_inner_bound']['lat'] ) / chunk_number

    # take the user_coords from address_to_lat_lng and get inner_boundary_coords
    # for the top_left_inner_bound and bottom_right_inner_bound
    start_position_x = user_coords['top_left_inner_bound']['lng']
    start_position_y = user_coords['top_left_inner_bound']['lat']

    next_position_x = user_coords['top_left_inner_bound']['lng'] + offset_x
    next_position_y = user_coords['top_left_inner_bound']['lat'] + offset_y

    # print statements city
    print "------------------------------------------------------------------"
    print "This is user_coords", user_coords
    print "This is offset_x, offset_y", offset_x, offset_y
    print "This is start_position", start_position_x, start_position_y
    print "This is next_position_x, next_position_y", next_position_x, next_position_y
    print "------------------------------------------------------------------"

    # test_query = Crime_Data_NYC.query.filter(and_(
    #         and_(
    #             Crime_Data_NYC.longitude >= start_position_x,
    #             Crime_Data_NYC.longitude < next_position_x),
    #         and_(
    #             Crime_Data_NYC.latitude > next_position_y,
    #             Crime_Data_NYC.latitude <= start_position_y)
    #         )
    #     ).order_by(Crime_Data_NYC.longitude.desc()).all()
    # print "Test query:"
    # print len(test_query)
    for i in range(chunk_number):
        # outer for loop, we will do looping column-wise [x] second
        for j in range(chunk_number):
            # inner for loop, we will do by looping row-wise [y] first
            crimes_in_grid = Crime_Data_NYC.query.filter(and_(
                    and_(
                        Crime_Data_NYC.longitude >= start_position_x,
                        Crime_Data_NYC.longitude < next_position_x),
                    and_(
                        Crime_Data_NYC.latitude > next_position_y,
                        Crime_Data_NYC.latitude <= start_position_y)
                    )
                ).all()
            print "Grid Lat: %s \tGrid Lng: %s \tNumber of Crimes: %s" % \
                (start_position_y, start_position_x, len(crimes_in_grid))

            # holds the data unique to that individual tile on the bounds grid
            square_data = {
                'start_lat': start_position_y,
                'start_lng': start_position_x,
                'end_lat': next_position_y,
                'end_lng': next_position_x
                }

            # get the next_position_y and next_position_x and insert it into 2d array
            # crime_array.append([start_position_y, start_position_x])
            # what do I need? I want to render the crimes in
            crime_array.append([square_data])
            crime_totals.append(len(crimes_in_grid))

            # bump up the offset in the y direction
            start_position_y = next_position_y
            next_position_y = next_position_y + offset_y
        # bump up the offset in the x direction
        next_position_x += offset_x

    # sorry, a little janky since I'm using two lists to do this part
    crime_array = calculate_crime_index(crime_array, crime_totals)


def calculate_crime_index(crime_array, crime_totals):
    """ Calculates the crime index based on the bounds of the route and appends
        those crime indices to the list of crimes in that route bound """

    # get the maximum crime_total that is present in the array, that's the number
    # that all of the values will be normalized against
    normalizer = max(crime_totals)

    # now loop through the the actual crime_array and append the crime_index
    # based on the normalizer value
    for i in range(len(crime_totals)):
        crime_index = float(crime_totals[i]) / normalizer
        crime_array[i].append(crime_index)

    return crime_array


def generate_bounds(user_coords):
    """ draws the bounds for safety analysis around what will be the
        user defined route """

    print "this is user_coords from generate_bounds", user_coords

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

    print "this is the top_left_coord and bottom_right_coord", \
                top_left_coord, bottom_right_coord
    return (top_left_coord, bottom_right_coord)


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
