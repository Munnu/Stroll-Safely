import json
from gmaps import Directions

api = Directions()

# start and end coordinates in directions
# reminder: results returns a list
results = api.directions((40.728783, -73.7897503),
                         (40.6497484, -73.97767999999999))

print json.dumps(results, indent=2)
