from math import cos, sin, pi, radians

# this works compared to the others.

# cos(a) = cos(30 degrees) = cos(pi/6 radians) = Sqrt(3)/2 = 0.866025.
# sin(a) = sin(30 degrees) = sin(pi/6 radians) = 1/2 = 0.5.
# cos(latitude) = cos(-0.31399 degrees) = cos(-0.00548016 radian) = 0.999984984.
# r = 100 meters.
# east displacement = 100 * 0.5 / 0.999984984 / 111111 = 0.000450007 degree.
# north displacement = 100 * 0.866025 / 111111 = 0.000779423 degree.
# rewritten
# east displacement = r * sin(radians(bearing)) / 111111
# north displacement = r * cos(radians(bearing)) / 111111


def find_point(latitude, longitude, bearing):
    distance = 118  # meters
    east_displacement = distance * sin(radians(bearing)) / 111111
    north_displacement = distance * cos(radians(bearing)) / 111111

    waypoint_latitude = latitude + north_displacement
    waypoint_longitude = longitude + east_displacement

    return "lat:", waypoint_latitude, "lng:", waypoint_longitude

print "original:", 40.7539472, -73.9811953
print find_point(40.7539472, -73.9811953, 0), 0, "north"
print find_point(40.7539472, -73.9811953, 90), 90, "east"
print find_point(40.7539472, -73.9811953, 180), 180, "south"
print find_point(40.7539472, -73.9811953, 270), 270, "west"
