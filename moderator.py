class Moderator:
    def __init__(self, nickname, password):
        self.nickname = nickname
        self.password = password

    def change_nickname(self, newnickname):
        self.nickname = newnickname