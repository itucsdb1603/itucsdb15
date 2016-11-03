class Hashtags:
    def __init__(self):
            self.hashtags = {}
            self.last_hashtag_id = 0

    def add_hashtag(self, hashtag):

            self.hashtags[self.last_hashtag_id] = hashtag
            hashtag._id = self.last_hashtag_id
            self.last_hashtag_id += 1

    def delete_hashtag(self, hashtag_id):
            del self.hashtags[hashtag_id]

    def get_hashtag(self, hashtag_id):
            return self.hashtags[hashtag_id]

    def get_hashtags(self):
            return self.hashtags