class HashtagContents:
    def __init__(self):
            self.contents = {}
            self.last_content_id = 0

    def add_content(self, content):
            self.last_content_id += 1
            self.contents[self.last_content_id] = content
            content._id = self.last_content_id

    def delete_content(self, content_id):
            del self.contents[content_id]

    def get_content(self, content_id):
            return self.contents[content_id]

    def get_contents(self):
            return self.contents
