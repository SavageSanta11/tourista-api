import unittest
import json
from app import app

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Hello, World!')

    def test_get_user_places(self):
        phone_number = "whatsapp:+917204671691"
        # Assuming the user with phone_number "1234567890" has places in the database
        response = self.app.get(f'/api/users/{phone_number}/places')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, list)

    def test_get_user_places_not_found(self):
        phone_number = "9876543210"
        # Assuming the user with phone_number "9876543210" does not exist in the database
        response = self.app.get(f'/api/users/{phone_number}/places')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "User not found")

    def test_update_user_places(self):
        phone_number = "1234567890"
        data = {
            "places": ["Place 1", "Place 2", "Place 3"]
        }
        response = self.app.patch(f'/api/users/{phone_number}/places', json=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Places updated successfully")

    def test_update_user_location(self):
        phone_number = "1234567890"
        data = {
            "location": {
                "lat": 40.7128,
                "long": -74.0060
            }
        }
        response = self.app.patch(f'/api/users/{phone_number}/location', json=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Location updated successfully")

    def test_remove_topmost_place(self):
        phone_number = "1234567890"
        response = self.app.patch(f'/api/users/{phone_number}/places/remove')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Topmost place removed successfully")

    def test_remove_topmost_place_empty_places_list(self):
        phone_number = "whatsapp:+18574924065"
        # Assuming the user with phone_number "0987654321" exists, but the places list is empty
        response = self.app.patch(f'/api/users/{phone_number}/places/remove')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertIn("message", data)
        self.assertEqual(data["message"], "No places found for the user or places list is empty")


if __name__ == '__main__':
    unittest.main()
