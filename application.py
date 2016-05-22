from flask import Flask, render_template, url_for, jsonify, request
from flask_restful import marshal_with, fields
from model import Crime_Data_NYC, NYC_Crimes_by_Geohash, connect_to_db
#from model import init_app

from middle import get_twenty, address_to_lat_lng

app = Flask(__name__)


@app.route('/')
def index():
    """ runs app name mainspace """
    return render_template("main.html")


@app.route('/geojson_sample.json')
def geojson_sample():
    """ return a geojson """
    return jsonify(construct())


@app.route('/start-end.json')
def parse_user_start_end():
    """ takes the user's start and end points in address form
        and convert to latitude, longitude """

    # retrieve parameters and get their data from the /start-end.json endpoint
    start = request.args.get('start')
    end = request.args.get('end')

    # assemble a dictionary to push into the address_to_lat_lng() function
    start_end_dict = {'start': start, 'end': end}

    # returns latitude and longitude of point A and point B
    lat_lng_dict = address_to_lat_lng(start_end_dict)

    return jsonify(lat_lng_dict)


@app.route('/directions-data.json', methods=['POST'])
def directionsData():
    """ This holds all of the leg information pertaining to the route
        and all of this other fancy stuff """

    directions_data = request.get_json()
    print "This is directions_data", directions_data

    return directions_data

@app.route('/crimes.json')
def crimes():
    """ return a json of crimes lat, longitude """
    # crimes_coords = {'crimes': [
    #         {'latitude': 40.7127837, 'longitude': -74.00594130000002},
    #         {'latitude': 40.57948579, 'longitude': -73.99844033},
    #         {'latitude': 40.83069115, 'longitude': -73.95586724}
    #         ]}
    crimes_coords = get_twenty()
    return jsonify(crimes_coords)

if __name__ == '__main__':
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    connect_to_db(app)
    app.run(debug=True)
