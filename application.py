from flask import Flask, render_template, url_for, jsonify
from flask_restful import marshal_with, fields
from model import Crime_Data_NYC, connect_to_db

app = Flask(__name__)

# at somep point our routes will be .jsons

mfields = {'type': fields.Raw,
            'features': fields.Raw}
@marshal_with(mfields)
def construct():
    constructed_json = {'type': 'FeatureCollection',
                        'features': [{
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [40.7282239, -73.79485160000002]
                                },
                                'properties': {
                                'prop0': 'value0'
                                }
                        }
                    ]}
    return constructed_json


@app.route('/')
def index():
    """ runs app name mainspace """
    return render_template("main.html")

@app.route('/geojson_sample.json')
def geojson_sample():
    """ return a geojson """
    return jsonify(construct())

@app.route('/crimes.json')
def crimes():
    """ return a json of crimes lat, longitude """
    crimes_coords = {'crimes': [
            {'latitude': 40.7127837, 'longitude': -74.00594130000002},
            {'latitude': 40.57948579, 'longitude': -73.99844033},
            {'latitude': 40.83069115, 'longitude': -73.95586724}
            ]}
    
    return jsonify(crimes_coords)

if __name__ == '__main__':
    app.run(debug=True)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    connect_to_db(app)
    app.run()
