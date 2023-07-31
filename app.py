from flask import Flask, request, jsonify
from pymongo import MongoClient

from db.models.user import User
import prometheus_client
from prometheus_client import Counter, generate_latest, start_http_server, Summary

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)  

app = Flask(__name__)

get_user_places_metric = Counter('get_user_places', 'Get User Places', ['phone_no'])
GET_PLACES_REQUEST_TIME = Summary('get_user_places_seconds', 'Time spent in GET user places ')

update_user_places_metric = Counter('update_user_places', 'Update User Places', ['phone_no'])
UPDATE_PLACES_REQUEST_TIME = Summary('update_user_places_seconds', 'Time spent in UPDATE user places')

get_user_location_metric = Counter('get_user_location', 'Get User Location', ['phone_no'])
GET_LOCATION_REQUEST_TIME = Summary('get_user_location_seconds', 'Time spent GET user location')

update_user_location_metric = Counter('update_user_location', 'Update User Location', ['phone_no'])
UPDATE_LOCATION_REQUEST_TIME = Summary('update_user_location_seconds', 'Time spent in GET user location')

remove_topmost_place_metric = Counter('remove_topmost_place', 'Remove Topmost Place', ['phone_no'])
REMOVE_PLACES_REQUEST_TIME = Summary('remove_places_seconds', 'Time spent in REMOVE topmost user place')
graphs['remove_topmost_place_metric'] = remove_topmost_place_metric

remove_specific_place_metric = Counter('remove_specific_place', 'Remove a Specific Place', ['phone_no'])
REMOVE__SPEC_PLACE_REQUEST_TIME = Summary('remove_specific_place_seconds', 'Time spent in REMOVE specific user place')
graphs['remove_specific_place_metric'] = remove_specific_place_metric


# root route
@app.route('/')
def hello_world():
    return 'Hello, World!'

uri = "mongodb+srv://aditikumaresan:C3C9qU2lASi1cDt4@tourista.rdze9hh.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
db = client['user_details']
collection = db['info']
  
# API endpoint to get all places for a user
@app.route('/api/users/<phone_number>/places', methods=['GET'])
@GET_PLACES_REQUEST_TIME.time()
def get_user_places(phone_number):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        get_user_places_metric.labels(phone_no=phone_number).inc()
        return jsonify(user.get('places', []))
    else:
        get_user_places_metric.labels(phone_no=phone_number).inc()
        return jsonify({"message": "User not found"}), 404


# API endpoint to update all places for a user
@app.route('/api/users/<phone_number>/places', methods=['PATCH'])
@UPDATE_PLACES_REQUEST_TIME.time()
def update_user_places(phone_number):
    data = request.get_json()
    if 'places' in data and isinstance(data['places'], list):
        # Retrieve existing user data from MongoDB
        user = collection.find_one({"phone_number": phone_number})
        if not user:
            # If user does not exist, create a new user document
            new_user = {
                "phone_number": phone_number,
                "places": data['places']
            }
            collection.insert_one(new_user)
            update_user_places_metric.labels(phone_no=phone_number).inc()
            return jsonify({"message": "New user created successfully"}), 201
        else:
            # If user exists, update the user's places list with the new list of places
            user['places'] = data['places']
            # Update user data in MongoDB
            collection.update_one({"phone_number": phone_number}, {"$set": user})
            update_user_places_metric.labels(phone_no=phone_number).inc()
            return jsonify({"message": "Places updated successfully"}), 200
    else:
        update_user_places_metric.labels(phone_no=phone_number).inc()
        return jsonify({"message": "Invalid data"}), 400

@app.route('/api/users/<phone_number>/location', methods=['GET'])
@GET_LOCATION_REQUEST_TIME.time()
def get_user_location(phone_number):
    # Retrieve existing user data from MongoDB
    user = collection.find_one({"phone_number": phone_number})
    if user and 'location' in user:
        get_user_location_metric.labels(phone_no=phone_number).inc()
        return jsonify(user['location']), 200
    else:
        get_user_location_metric.labels(phone_no=phone_number).inc()
        return jsonify({"message": "User not found or location not available"}), 404

@app.route('/api/users/<phone_number>/location', methods=['PATCH'])
@UPDATE_LOCATION_REQUEST_TIME.time()
def update_user_location(phone_number):
    data = request.get_json()
    if 'location' in data and isinstance(data['location'], dict) and 'lat' in data['location'] and 'long' in data['location'] and 'street_address' in data['location']:
        # Extract latitude and longitude from the location dictionary
        lat = data['location']['lat']
        long = data['location']['long']
        street_address = data['location']['street_address']

        # Retrieve existing user data from MongoDB
        user = collection.find_one({"phone_number": phone_number})
        if not user:
            # If user does not exist, create a new user document
            new_user = {
                "phone_number": phone_number,
                "location": {"lat": lat, "long": long, "street_address": street_address}
            }
            collection.insert_one(new_user)
            update_user_location_metric.labels(phone_no=phone_number).inc()
            return jsonify({"message": "New user created successfully"}), 200
        else:
            # If user exists, update the user's location with the new location
            user['location'] = {"lat": lat, "long": long, "street_address": street_address}
            # Update user data in MongoDB
            collection.update_one({"phone_number": phone_number}, {"$set": user})
            update_user_location_metric.labels(phone_no=phone_number).inc()
            return jsonify({"message": "Location updated successfully"}), 200
    else:
        update_user_location_metric.labels(phone_no=phone_number).inc()
        return jsonify({"message": "Invalid data"}), 400

@app.route('/api/users/<phone_number>/places/remove', methods=['PATCH'])
@REMOVE_PLACES_REQUEST_TIME.time()
def remove_topmost_place(phone_number):
    # Retrieve existing user data from MongoDB
    user = collection.find_one({"phone_number": phone_number})
    if not user:
        remove_topmost_place_metric.labels(phone_no=phone_number).inc()
        return jsonify({"message": "User not found"}), 404

    # Remove the topmost element from the places array
    if 'places' in user and isinstance(user['places'], list) and len(user['places']) > 0:
        topmost_place = user['places'].pop(0)  # Remove the first element
        # Update user data in MongoDB
        collection.update_one({"phone_number": phone_number}, {"$set": user})
        remove_topmost_place_metric.labels(phone_no=phone_number).inc()
        return jsonify({"place": topmost_place}), 200
    else:
        remove_topmost_place_metric.labels(phone_no=phone_number).inc()
        return jsonify({"message": "No places found for the user or places list is empty"}), 400


@app.route('/api/users/<phone_number>/places/remove/<place_name>', methods=['PATCH'])
@REMOVE__SPEC_PLACE_REQUEST_TIME.time()
def remove_place_by_name(phone_number, place_name):
    # Retrieve existing user data from MongoDB
    user = collection.find_one({"phone_number": phone_number})
    if not user:
        remove_specific_place_metric.labels(phone_no=phone_number).inc()
        graphs['remove_specific_place_metric'] = remove_specific_place_metric
        return jsonify({"message": "User not found"}), 404

    # Check if the user has any places
    if 'places' not in user or not isinstance(user['places'], list) or len(user['places']) == 0:
        remove_specific_place_metric.labels(phone_no=phone_number).inc()
        graphs['remove_specific_place_metric'] = remove_specific_place_metric
        return jsonify({"message": "No places found for the user or places list is empty"}), 400

    # Find and remove the place from the user's places list based on the name
    found_place = None
    for place in user['places']:
        if place.get('title') == place_name:
            found_place = place
            user['places'].remove(place)
            break

    if found_place is None:
        remove_specific_place_metric.labels(phone_no=phone_number).inc()
        graphs['remove_specific_place_metric'] = remove_specific_place_metric
        return jsonify({"message": f"Place with name '{place_name}' not found in the user's places list"}), 404

    # Update user data in MongoDB
    collection.update_one({"phone_number": phone_number}, {"$set": user})
    remove_specific_place_metric.labels(phone_no=phone_number).inc()
    graphs['remove_specific_place_metric'] = remove_specific_place_metric
    return jsonify({"message": f"Place '{place_name}' removed successfully"}), 200

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    start_http_server(8009)
    app.run(port=4000)
