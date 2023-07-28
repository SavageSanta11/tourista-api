import unittest
import json
from flask import Flask
from flask.testing import FlaskClient
from pymongo import MongoClient
from app import app, collection

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        # Clear the collection after each test
        collection.delete_many({})

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Hello, World!')

    def test_get_user_places(self):
        phone_number = "1234567890"
        # Add a user with places to the collection
        user = {
            "phone_number": phone_number,
            "places": ["Place 1", "Place 2", "Place 3"]
        }
        collection.insert_one(user)

        response = self.app.get(f'/api/users/{phone_number}/places')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(data, user['places'])

    def test_update_user_places(self):
        phone_number = "1234567890"
        places = ["Place 1", "Place 2", "Place 3"]
        data = {
            "places": places
        }

        response = self.app.patch(f'/api/users/{phone_number}/places', json=data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "New user created successfully")

        # Check if the user document is created in the collection
        user = collection.find_one({"phone_number": phone_number})
        self.assertIsNotNone(user)
        self.assertEqual(user["places"], places)

        # Update the places for the user
        new_places = ["Place 4", "Place 5"]
        data = {
            "places": new_places
        }

        response = self.app.patch(f'/api/users/{phone_number}/places', json=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Places updated successfully")

        # Check if the places are updated in the user document
        user = collection.find_one({"phone_number": phone_number})
        self.assertIsNotNone(user)
        self.assertEqual(user["places"], new_places)

    def test_get_user_location(self):
        phone_number = "1234567890"
        location = {
            "lat": 123.456,
            "long": 456.789,
            "street_address": "123 Main St"
        }
        # Add a user with location to the collection
        user = {
            "phone_number": phone_number,
            "location": location
        }
        collection.insert_one(user)

        response = self.app.get(f'/api/users/{phone_number}/location')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data, location)

    def test_update_user_location(self):
        phone_number = "1234567890"
        location = {
            "lat": 123.456,
            "long": 456.789,
            "street_address": "123 Main St"
        }
        data = {
            "location": location
        }

        response = self.app.patch(f'/api/users/{phone_number}/location', json=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "New user created successfully")

        # Check if the user document is created in the collection
        user = collection.find_one({"phone_number": phone_number})
        self.assertIsNotNone(user)
        self.assertEqual(user["location"], location)

        # Update the location for the user
        new_location = {
            "lat": 789.123,
            "long": 321.654,
            "street_address": "456 Elm St"
        }
        data = {
            "location": new_location
        }

        response = self.app.patch(f'/api/users/{phone_number}/location', json=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Location updated successfully")

        # Check if the location is updated in the user document
        user = collection.find_one({"phone_number": phone_number})
        self.assertIsNotNone(user)
        self.assertEqual(user["location"], new_location)

    def test_remove_topmost_place(self):
        phone_number = "1234567890"
        places = ["Place 1", "Place 2", "Place 3"]
        # Add a user with places to the collection
        user = {
            "phone_number": phone_number,
            "places": places
        }
        collection.insert_one(user)

        response = self.app.patch(f'/api/users/{phone_number}/places/remove')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("place", data)
        self.assertEqual(data["place"], places[0])

        # Check if the topmost place is removed from the user document
        user = collection.find_one({"phone_number": phone_number})
        self.assertIsNotNone(user)
        self.assertEqual(user["places"], places[1:])

if __name__ == '__main__':
    unittest.main()
