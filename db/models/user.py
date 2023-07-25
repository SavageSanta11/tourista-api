class User:
    def __init__(self, phone_number, places=None, location=None):
        self.phone_number = phone_number
        self.places = places if places is not None else []
        self.location = location if location is not None else {}