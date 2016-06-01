from math import asin, cos, sin, atan2, pi


def find_pt(start, dist, bearing):
    # R = 3437.75  # Earth's radius in nautical miles
    R = 3959  # Earth's radius in miles
    lat_start = start[0]
    lon_start = start[1]

    # distance is in nautical miles
    # from stackoverflow:
    # http://gis.stackexchange.com/questions/5821/calculating-lat-lng-x-miles-from-point
    # which it's really from: http://williams.best.vwh.net/avform.htm#LL

    # lat=asin(sin(lat1)*cos(d)+cos(lat1)*sin(d)*cos(tc))
    #  IF (cos(lat)=0)
    #     lon=lon1      // endpoint a pole
    #  ELSE
    #     lon=mod(lon1-asin(sin(tc)*sin(d)/cos(lat))+pi,2*pi)-pi
    #  ENDIF

    lat = lat_start + asin(sin(lat_start) * cos(dist/R) + cos(lat_start) * sin(dist/R) * cos(bearing))
    if (cos(lat) == 0):
        lon = lon_start
    # lon = ((lon_start-asin(sin(bearing)*sin(dist)/cos(lat))+pi) % 2*pi)-pi  # math domain error
    lon = lon_start + atan2(sin(bearing) * sin(dist/R) * cos(lat_start), cos(dist/R) - sin(lat_start) * sin(lat))
    return lat, lon

print "Point is: ", 40.7539472, -73.9811953
print
print find_pt([40.7539472, -73.9811953], 1, 0), 1
print find_pt([40.7539472, -73.9811953], 5, 90), 5
print find_pt([40.7539472, -73.9811953], 118, 180), 118
print find_pt([40.7539472, -73.9811953], 10000, 270), 10000

print "Stackoverflow says a geohash precision of 7 is 118 meters"
print find_pt([40.7539472, -73.9811953], 118, 0), 118, 0
print find_pt([40.7539472, -73.9811953], 118, 90), 118, 90
print find_pt([40.7539472, -73.9811953], 118, 180), 118, 180
print find_pt([40.7539472, -73.9811953], 118, 270), 118, 270
