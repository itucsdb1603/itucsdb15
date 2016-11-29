class PlaceList:
    def __init__(self):
            self.places = {}
            self.last_place_id = 0

    def add_place(self, place):
            self.last_place_id += 1
            self.places[self.last_place_id] = place
            place._id = self.last_place_id

    def delete_place(self, place_id):
            del self.places[place_id]

    def get_place(self, place_id):
            return self.places[place_id]

    def get_places(self):
            return self.places
