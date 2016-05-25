from math import cos, sin


def find_point(latitude, longitude, direction):
    DEGREE_CONSTANT = 111111
    DISTANCE_INCREMENT = 118  # meters
    if direction == 'west':
        bearing = 0  # this will change based on conditionals of delta x-y
    elif direction == 'east':
        bearing = 180  # check to see if this yields good results
    elif direction == 'north':
        bearing = 90
    elif direction == 'south':
        bearing = 270

    waypoint_lat = latitude + (DISTANCE_INCREMENT * sin(bearing)) / 110540
    waypoint_lng = longitude + (DISTANCE_INCREMENT * cos(bearing)) / (111320 * cos(latitude))

    return waypoint_lat, waypoint_lng

print 40.7539472, -73.9811953
print find_point(40.7539472, -73.9811953, 'north'), 'north'
print find_point(40.7539472, -73.9811953, 'south'), 'south'
print find_point(40.7539472, -73.9811953, 'east'), 'east'
print find_point(40.7539472, -73.9811953, 'west'), 'west'
