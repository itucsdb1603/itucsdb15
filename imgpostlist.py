class ImgPostList:
    def __init__(self):
            self.imgposts = {}
            self.last_imgPost_id = 0

    def add_imgPost(self, imgPost):
            self.last_imgPost_id += 1
            self.imgposts[self.last_imgPost_id] = imgPost
            imgPost._id = self.last_imgPost_id

    def delete_imgPost(self, imgPost_id):
            del self.imgposts[imgPost_id]

    def get_imgPost(self, imgPost_id):
            return self.imgposts[imgPost_id]

    def get_imgPostList(self):
            return self.imgposts