from flask import current_app as app
from flask_login import UserMixin

class Moderator(UserMixin):
    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.nickname

    @property
    def is_active(self):
        return self.active


