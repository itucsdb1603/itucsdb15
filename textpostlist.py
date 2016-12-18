import psycopg2 as dbapi2
from textpost import TextPost
from flask import current_app as app
from flask_login import UserMixin
from _sqlite3 import Row

class TextPostList:
    def __init__(self):
            self.last_key = None

    def add_TextPost(self, textPost):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO TEXTPOSTS (CONTENT, WRITER) VALUES (%s, %s)"""
                cursor.execute(query, (textPost.content, textPost.writer))
                connection.commit()

    def delete_TextPost(self, TextPost_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""DELETE FROM TEXTPOSTS WHERE (POSTID = (%s))"""
                cursor.execute(statement, (TextPost_id,))
                connection.commit()

    def update_TextPost(self, TextPost_id, new_content):
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""UPDATE TEXTPOSTS
                SET CONTENT = (%s)
                WHERE (POSTID = (%s))"""
                cursor.execute(statement, (new_content, TextPost_id,))
                connection.commit()

    def get_TextPost(self, content):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT POSTID FROM TEXTPOSTS WHERE (CONTENT = (%s))"""
                cursor.execute(query, (content, ))
                TextPost_id = cursor.fetchone()  
                connection.commit()
            return TextPost_id

    def get_TextPostList(self):
            with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               query = """SELECT POSTID, CONTENT, WRITER, NICKNAME FROM TEXTPOSTS JOIN
                MODERATORS ON WRITER=ID
                ORDER BY POSTID"""
               cursor.execute(query)
               TextPostTable = [(id, TextPost(content, writer), modname)
                          for id, content, writer, modname in cursor]
            return TextPostTable
        
    def get_TextPostListofMod(self, writer):
            with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               query = """SELECT POSTID, CONTENT, WRITER, NICKNAME FROM TEXTPOSTS JOIN
                MODERATORS ON WRITER=ID
                WHERE WRITER = (%s)
                ORDER BY POSTID"""
               cursor.execute(query, (writer,))
               TextPostTableofMod = [(id, TextPost(content, writer), modname)
                          for id, content, writer, modname in cursor]
            return TextPostTableofMod