from flask import Flask, request, jsonify
from pymongo import MongoClient

from db.models.user import User

from prometheus_client import Counter, generate_latest
  
app = Flask(__name__)
  
# root route
@app.route('/')
def hello_world():
    return 'Hello, World!'

uri = "mongodb+srv://aditikumaresan:C3C9qU2lASi1cDt4@tourista.rdze9hh.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)

# Create database named demo if they don't exist already
db = client['user_details']
  
# Create collection named data if it doesn't exist already
collection = db['info']
  
# API endpoint to get all places for a user
@app.route('/api/users/<phone_number>/places', methods=['GET'])
def get_user_places(phone_number):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        return jsonify(user.get('places', []))
    else:
        return jsonify({"message": "User not found"}), 404


# API endpoint to update all places for a user
@app.route('/api/users/<phone_number>/places', methods=['PATCH'])
def update_user_places(phone_number):
    data = request.get_json()
    print(data)
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
            return jsonify({"message": "New user created successfully"}), 201
        else:
            # If user exists, update the user's places list with the new list of places
            user['places'] = data['places']
            # Update user data in MongoDB
            collection.update_one({"phone_number": phone_number}, {"$set": user})
            return jsonify({"message": "Places updated successfully"}), 200
    else:
        return jsonify({"message": "Invalid data"}), 400

@app.route('/api/users/<phone_number>/location', methods=['GET'])
def get_user_location(phone_number):
    # Retrieve existing user data from MongoDB
    user = collection.find_one({"phone_number": phone_number})
    if user and 'location' in user:
        return jsonify(user['location']), 200
    else:
        return jsonify({"message": "User not found or location not available"}), 404

@app.route('/api/users/<phone_number>/location', methods=['PATCH'])
def update_user_location(phone_number):
    data = request.get_json()
    print(data)
    if 'location' in data and isinstance(data['location'], dict) and 'lat' in data['location'] and 'long' in data['location']:
        # Extract latitude and longitude from the location dictionary
        lat = data['location']['lat']
        long = data['location']['long']

        # Retrieve existing user data from MongoDB
        user = collection.find_one({"phone_number": phone_number})
        if not user:
            # If user does not exist, create a new user document
            new_user = {
                "phone_number": phone_number,
                "location": {"lat": lat, "long": long}
            }
            collection.insert_one(new_user)
            return jsonify({"message": "New user created successfully"}), 200
        else:
            # If user exists, update the user's location with the new location
            user['location'] = {"lat": lat, "long": long}
            # Update user data in MongoDB
            collection.update_one({"phone_number": phone_number}, {"$set": user})
            return jsonify({"message": "Location updated successfully"}), 200
    else:
        return jsonify({"message": "Invalid data"}), 400

@app.route('/api/users/<phone_number>/places/remove', methods=['PATCH'])
def remove_topmost_place(phone_number):
    # Retrieve existing user data from MongoDB
    user = collection.find_one({"phone_number": phone_number})
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Remove the topmost element from the places array
    if 'places' in user and isinstance(user['places'], list) and len(user['places']) > 0:
        topmost_place = user['places'].pop(0)  # Remove the first element
        # Update user data in MongoDB
        collection.update_one({"phone_number": phone_number}, {"$set": user})
        return jsonify({"place": topmost_place}), 200
    else:
        return jsonify({"message": "No places found for the user or places list is empty"}), 400

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(port=4000)