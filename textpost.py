class TextPost:
    def __init__(self, content, writer):
        self.content = content
        self.writer = writer
    def change_textpost(self, new_content):
        self.content = new_content