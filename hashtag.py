from hashtagContents import HashtagContents
class Hashtag:
    def __init__(self, name):
        self.name = name
        self.hashtagContents = HashtagContents()

    def update_name(self, updatedHashtag):
        self.name = updatedHashtag