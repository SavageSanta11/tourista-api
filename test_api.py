import unittest
from unittest.mock import patch
from app import (
    get_user_places,
    update_user_places,
    get_user_location,
    update_user_location,
    remove_topmost_place,
    remove_place_by_name,
    get_chat_history,
    update_chat_history,
    get_user_interest,
    store_user_interest,
    app,
)

# Import mongomock's MongoClient
from mongomock import MongoClient


class TestAppEndpoints(unittest.TestCase):
    def setUp(self):
        # Use mongomock's MongoClient for testing
        self.mongo_client = MongoClient()
        self.db = self.mongo_client["user_details"]
        app.config["TESTING"] = True
        self.app = app.test_client()

    def tearDown(self):
        # Clear the database after each test
        self.mongo_client.drop_database("user_details")

    def test_get_user_places_existing_user(self):
        # Arrange
        phone_number = "1234567890"
        test_places = [{"title": "Place 1"}, {"title": "Place 2"}]
        self.db["info"].insert_one({"phone_number": phone_number, "places": test_places})

        # Act
        response = self.app.get(f"/api/users/{phone_number}/places")
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(data, test_places)

    def test_get_user_places_user_not_found(self):
        # Arrange
        phone_number = "1234567890"

        # Act
        response = self.app.get(f"/api/users/{phone_number}/places")
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 404)
        self.assertEqual(data, {"message": "User not found"})

    def test_update_user_places_existing_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"places": [{"title": "Place 1"}, {"title": "Place 2"}]}
        self.db["info"].insert_one({"phone_number": phone_number})

        # Act
        response = self.app.patch(
            f"/api/users/{phone_number}/places", json=test_data
        )
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"message": "Places updated successfully"})

    def test_update_user_places_new_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"places": [{"title": "Place 1"}, {"title": "Place 2"}]}

        # Act
        response = self.app.patch(
            f"/api/users/{phone_number}/places", json=test_data
        )
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 201)
        self.assertEqual(data, {"message": "New user created successfully"})

    def test_get_user_location_existing_user_with_location(self):
        # Arrange
        phone_number = "1234567890"
        test_location = {
            "lat": 40.7128,
            "long": -74.0060,
            "street_address": "New York City, NY",
        }
        self.db["info"].insert_one(
            {"phone_number": phone_number, "location": test_location}
        )

        # Act
        response = self.app.get(f"/api/users/{phone_number}/location")
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(data, test_location)

    def test_get_user_location_existing_user_without_location(self):
        # Arrange
        phone_number = "1234567890"
        self.db["info"].insert_one({"phone_number": phone_number})

        # Act
        response = self.app.get(f"/api/users/{phone_number}/location")
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 404)
        self.assertEqual(
            data, {"message": "User not found or location not available"}
        )

    def test_update_user_location_existing_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {
            "location": {
                "lat": 40.7128,
                "long": -74.0060,
                "street_address": "New York City, NY",
            }
        }
        self.db["info"].insert_one({"phone_number": phone_number})

        # Act
        response = self.app.patch(
            f"/api/users/{phone_number}/location", json=test_data
        )
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"message": "Location updated successfully"})

    def test_update_user_location_new_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {
            "location": {
                "lat": 40.7128,
                "long": -74.0060,
                "street_address": "New York City, NY",
            }
        }

        # Act
        response = self.app.patch(
            f"/api/users/{phone_number}/location", json=test_data
        )
        data = response.get_json()
        status_code = response.status_code

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"message": "New user created successfully"})

    # Continue with other tests for remaining endpoints...


if __name__ == "__main__":
    unittest.main()
