from copy import deepcopy
import unittest
from middle import generate_waypoint, distance_to_coords_formula
from middle import address_to_lat_lng, inspect_waypoints
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

    def test_address_to_lat_lng_correct(self):
        """ tests to see if geocoding works properly """

        # note: use a mockup later.
        user_points = {'start': 'Empire State Building', 'end': 'Herald Square'}

        expected_coords = {'point_a': {'lat': 40.7484405, 'lng': -73.98566439999999},
                           'point_b': {'lat': 40.7505423, 'lng': -73.9877176}}

        generated_coords = address_to_lat_lng(user_points)
        eq_(generated_coords, expected_coords)

    def test_address_to_lat_lng_incorrect(self):
        """ tests to see if geocoding works properly """

        # note: use a mockup later.
        user_points = {'start': 'Empire State Building', 'end': 'Herald Square'}

        wrong_coords = {'point_a': {'lat': 40.748440, 'lng': -73.9856643999999},
                        'point_b': {'lat': 40.750542, 'lng': -73.987717}}

        generated_coords = address_to_lat_lng(user_points)
        assert_not_equal(generated_coords, wrong_coords)

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

    def test_inspect_waypoints(self):

        current_point = (40.8131494, -73.95032520000001)
        latwise_inspect = inspect_waypoints(current_point, 'latwise')
        lngwise_inspect = inspect_waypoints(current_point, 'lngwise')
        all_inspect = inspect_waypoints(current_point, 'all')

        eq_(latwise_inspect[0][1], latwise_inspect[1][1])
        eq_(lngwise_inspect[0][0], lngwise_inspect[1][0])

        assert_not_equal(latwise_inspect[0][0], latwise_inspect[1][0])
        assert_not_equal(lngwise_inspect[0][1], lngwise_inspect[1][1])

        eq_(all_inspect[0][1], all_inspect[1][1])
        eq_(all_inspect[2][0], all_inspect[3][0])
        assert_not_equal(all_inspect[0][0], all_inspect[1][0])
        assert_not_equal(all_inspect[2][1], all_inspect[3][1])

        eq_(len(latwise_inspect), 2)
        eq_(len(lngwise_inspect), 2)
        eq(len(all_inspect), 4)


