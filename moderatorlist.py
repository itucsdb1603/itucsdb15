class ModeratorList:
    def __init__(self):
            self.moderators = {}
            self.last_mod_id = 0

    def add_moderator(self, moderator):
            self.last_mod_id += 1
            self.moderators[self.last_mod_id] = moderator
            moderator._id = self.last_mod_id

    def delete_moderator(self, mod_id):
            del self.moderators[mod_id]

    def get_moderator(self, mod_id):
            return self.moderators[mod_id]

    def get_moderators(self):
            return self.moderators
