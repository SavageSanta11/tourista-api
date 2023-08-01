import unittest
from unittest.mock import patch
from app import (
    update_user_places,
    update_user_location,
    update_chat_history,
    get_user_interest,
    store_user_interest,
    app,
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

    
    def test_remove_topmost_place_existing_user_without_places(self):
        # Arrange
        phone_number = "1234567890"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.patch(f"/api/users/{phone_number}/places/remove")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 400)
            self.assertEqual(
                data, {"message": "No places found for the user or places list is empty"}
            )

    def test_remove_topmost_place_user_not_found(self):
        # Arrange
        phone_number = "1234567890"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.patch(f"/api/users/{phone_number}/places/remove")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 404)
            self.assertEqual(data, {"message": "User not found"})

    def test_remove_place_by_name_existing_user_with_matching_place_name(self):
        # Arrange
        phone_number = "1234567890"
        place_name = "Place 1"
        test_places = [{"title": "Place 1"}, {"title": "Place 2"}]
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number, "places": test_places}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.patch(f"/api/users/{phone_number}/places/remove/{place_name}")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 200)
            self.assertEqual(data, {"message": f"Place '{place_name}' removed successfully"})

    def test_remove_place_by_name_existing_user_without_matching_place_name(self):
        # Arrange
        phone_number = "1234567890"
        place_name = "Place 3"
        test_places = [{"title": "Place 1"}, {"title": "Place 2"}]
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number, "places": test_places}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.patch(f"/api/users/{phone_number}/places/remove/{place_name}")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 404)
            self.assertEqual(
                data, {"message": f"Place with name '{place_name}' not found in the user's places list"}
            )

    def test_remove_place_by_name_existing_user_without_places(self):
        # Arrange
        phone_number = "1234567890"
        place_name = "Place 1"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.patch(f"/api/users/{phone_number}/places/remove/{place_name}")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 400)
            self.assertEqual(
                data, {"message": "No places found for the user or places list is empty"}
            )

    def test_remove_place_by_name_user_not_found(self):
        # Arrange
        phone_number = "1234567890"
        place_name = "Place 1"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.patch(f"/api/users/{phone_number}/places/remove/{place_name}")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 404)
            self.assertEqual(data, {"message": "User not found"})

    def test_get_chat_history_existing_user_with_chat_history(self):
        # Arrange
        phone_number = "1234567890"
        test_chat_history = [{"message": "Hello"}, {"message": "Hi"}]
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number, "chat_history": test_chat_history}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.get(f"/api/users/{phone_number}/chat_history")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 200)
            self.assertEqual(data, test_chat_history)

    def test_get_chat_history_existing_user_without_chat_history(self):
        # Arrange
        phone_number = "1234567890"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.get(f"/api/users/{phone_number}/chat_history")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 404)
            self.assertEqual(
                data, {"message": "User not found or chat history not available"}
            )

    def test_update_chat_history_existing_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"chat_history": [{"message": "Hello"}, {"message": "Hi"}]}
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = update_chat_history(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)

    def test_update_chat_history_new_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"chat_history": [{"message": "Hello"}, {"message": "Hi"}]}
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = update_chat_history(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)

    def test_get_user_interest_existing_user_with_interest(self):
        # Arrange
        phone_number = "1234567890"
        test_interest = "Traveling"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number, "interest": test_interest}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.get(f"/api/users/{phone_number}/interest")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 200)
            self.assertEqual(data, {"interest": test_interest})

    def test_get_user_interest_existing_user_without_interest(self):
        # Arrange
        phone_number = "1234567890"
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Act
            response = self.app.get(f"/api/users/{phone_number}/interest")
            data = response.get_json()
            status_code = response.status_code

            # Assert
            self.assertEqual(status_code, 404)
            self.assertEqual(
                data, {"message": "User not found or interest not available"}
            )

    def test_store_user_interest_existing_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"interest": "Traveling"}
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = {"phone_number": phone_number}

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = store_user_interest(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)

    def test_store_user_interest_new_user(self):
        # Arrange
        phone_number = "1234567890"
        test_data = {"interest": "Traveling"}
        mock_collection = mock.create_autospec(Collection)
        mock_collection.find_one.return_value = None

        # Mock the MongoDB collection
        with patch("app.collection", mock_collection):
            # Use the test_request_context to mock the Flask app
            with app.test_request_context(json=test_data):
                # Act
                response = store_user_interest(phone_number)
                status_code = response[1]

                # Assert
                self.assertEqual(status_code, 200)


if __name__ == "__main__":
    unittest.main()
