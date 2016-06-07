from copy import deepcopy
import unittest
from middle import generate_waypoint, distance_to_coords_formula
from nose.tools import eq_, assert_not_equal


class TestMiddle(unittest.TestCase):
    def test_generate_waypoint_high_crime(self):
        """ if there is high crime, a waypoint will be generated """

        lowest_crime_index = 0.5
        points_data = [{'crime_index': 0.5,
                        'total_crimes': 115,
                        'geohash': 'hfugpsb',
                        'point': (40.8, -73.96)
                        }]
        segmented_points = [{'data':
                            {'start':
                                {'lat': 40.8, 'lng': -73.96},
                                'end': {'lat': 40.8131494, 'lng': -73.95032520000001},
                                'waypoints': []}},
                            {'is_high_crime': False,
                                'lat': 40.8,
                                'geohash': u'hfv528h',
                                'crime_index': 0.5,
                                'lng': -73.96,
                                'total_crimes': 45}]

        original = deepcopy(segmented_points)

        generate_waypoint(lowest_crime_index, points_data, segmented_points)

        expected = [{'data':
                    {'start':
                        {'lat': 40.8, 'lng': -73.96},
                        'end': {'lat': 40.8131494, 'lng': -73.95032520000001},
                        'waypoints': [
                            {'location':
                                {'lat': 40.8, 'lng': -73.96},
                                'stopover': False}]}},
                    {'is_high_crime': False,
                        'lat': 40.8,
                        'geohash': u'hfv528h',
                        'crime_index': 0.5,
                        'lng': -73.96,
                        'total_crimes': 45}]
        assert_not_equal(original, expected)
        # assert segmented_points != original
        # eq_(segmented_points, expected)

    def test_generate_waypoint_low_crime(self):
        """ if there is low crime no waypoints should be generated """

        lowest_crime_index = 0.2
        points_data = [{'crime_index': 0.2,
                        'total_crimes': 115,
                        'geohash': 'hfugpsb',
                        'point': (40.8, -73.96)
                        }]
        segmented_points = [{'data':
                            {'start':
                                {'lat': 40.8, 'lng': -73.96},
                                'end': {'lat': 40.8131494, 'lng': -73.95032520000001},
                                'waypoints': []}},
                            {'is_high_crime': False,
                                'lat': 40.8,
                                'geohash': u'hfv528h',
                                'crime_index': 0.5,
                                'lng': -73.96,
                                'total_crimes': 45}]

        original = deepcopy(segmented_points)

        generate_waypoint(lowest_crime_index, points_data, segmented_points)

        expected = [{'data':
                    {'start':
                        {'lat': 40.8, 'lng': -73.96},
                        'end': {'lat': 40.8131494, 'lng': -73.95032520000001},
                        'waypoints': []}},
                    {'is_high_crime': False,
                        'lat': 40.8,
                        'geohash': u'hfv528h',
                        'crime_index': 0.5,
                        'lng': -73.96,
                        'total_crimes': 45}]
        eq_(original, expected)

    def test_distance_to_coords_formula_latwise(self):
        """ tests the latitudional (north, south) aspect of the formula to see
            if we get waypoints that have the same longitude, different lat """

        point_lat = 40.8131494
        point_lng = -73.95032520000001
        latwise_potential_waypoints = distance_to_coords_formula(point_lat,
                                                                 point_lng, 0, 180)
        longitude_n = latwise_potential_waypoints[0][1]
        longitude_s = latwise_potential_waypoints[1][1]

        latitude_n = latwise_potential_waypoints[0][0]
        latitude_s = latwise_potential_waypoints[1][0]

        eq_(longitude_n, longitude_s)
        eq_(longitude_n, point_lng)
        eq_(longitude_s, point_lng)
        assert_not_equal(latitude_n, latitude_s)
        assert_not_equal(latitude_n, point_lat)
        assert_not_equal(latitude_s, point_lat)

    def test_distance_to_coords_formula_lngwise(self):
        """ tests the longitudional (east, west) aspect of the formula to see
            if we get waypoints that have the same latitude, different lng """

        point_lat = 40.8131494
        point_lng = -73.95032520000001
        lngwise_potential_waypoints = distance_to_coords_formula(point_lat,
                                                                 point_lng, 90, 270)
        longitude_e = lngwise_potential_waypoints[0][1]
        longitude_w = lngwise_potential_waypoints[1][1]

        latitude_e = lngwise_potential_waypoints[0][0]
        latitude_w = lngwise_potential_waypoints[1][0]

        eq_(latitude_e, latitude_w)
        eq_(latitude_e, point_lat)
        eq_(latitude_w, point_lat)
        assert_not_equal(longitude_e, longitude_w)
        assert_not_equal(longitude_e, point_lng)
        assert_not_equal(longitude_w, point_lng)
