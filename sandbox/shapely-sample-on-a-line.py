import urllib
import json
import sys
from shapely.geometry import LineString
from gmaps import Directions, Geocoding
from key import key


# print json.dumps(data, indent=2)

# # Load some sample data from the Google Directions API. In this case, we're going
# # from the Brooklyn Museum to Resistor.
# BASE_URL = "https://maps.googleapis.com/maps/api/directions/json?"
# params = {
#     'origin': '200 Eastern Parkway, Brooklyn, NY',
#     'destination': '87 3rd Ave, Brooklyn, NY',
#     'key': 'YOUR_KEY',
#     'mode': 'walking'
# }

# url = BASE_URL + urllib.urlencode(params)
# print url
# fh = urllib.urlopen(url)
# response = fh.read()
# fh.close()

# data = json.loads(response)

api = Directions()

data = api.directions(
                        '200 Eastern Parkway, Brooklyn, NY',
                        '87 3rd Ave, Brooklyn, NY',
                        mode="walking"
                        )


if len(data[0]) == 0:
    print "No routes found!"
    # Dammit.
    print sys.exit(0)

# For this example, we're only going to look at the first route but you will
# probably want to do this for all routes.
route = data[0]
print "length of route, legs", len(route['legs'])
first = True
line_points = []
for leg in route['legs']:
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
print "line_points", line_points
route_line = LineString(line_points)
# For fun, print the length. We don't need it.
print "Line length ", route_line.length

# The first point is the starting point.
print "Line start ", repr(route_line.coords[0])
# Let's traverse the line, by looking at points that are one tenth of the way
# down the line, then two tenths, and so on. The interpolate function treats
# distance_along_line as a fraction of the length when normalized is true,
# so 0.1 means one tenth of the length.
distance_along_line = 0.1
for i in range(1, 11):
    point = route_line.interpolate(distance_along_line, normalized=True)
    print "Point ", i, point
    distance_along_line += 0.1
# Since we used 1/10 the distance, the last point should be equal to the
# line end value.
print "Line end ", repr(route_line.coords[-1])

# Note: the output of interpolate is a Point data type but you can get the
# individual members like so:
point = route_line.interpolate(distance_along_line, normalized=True)
lat = point.x
lng = point.y
print "lat, lng", lat, lng