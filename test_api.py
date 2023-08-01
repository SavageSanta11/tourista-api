import unittest
from unittest.mock import patch
from app import (
    update_user_places,
    update_user_location,
    app
)
from pymongo.collection import Collection
from mock import mock


class TestAppEndpoints(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()

    def test_get_user_places_existing_user(self):
        # Arrange
        phone_number = "1234567890"
        test_places = [{"title": "Place 1"}, {"title": "Place 2"}]
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number, "places": test_places}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
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
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
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
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = update_user_places(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)

    def test_update_user_places_new_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"places": [{"title": "Place 1"}, {"title": "Place 2"}]}
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = update_user_places(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 201)

    def test_get_user_location_existing_user_with_location(self):
        # Arrange
        phone_number = "1234567890"
        test_location = {
            "lat": 40.7128,
            "long": -74.0060,
            "street_address": "New York City, NY",
        }
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number, "location": test_location}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
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
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
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
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = update_user_location(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)

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
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = update_user_location(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)

    # Continue with other tests for remaining endpoints...


if __name__ == "__main__":
    unittest.main()
