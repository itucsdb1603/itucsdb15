import psycopg2 as dbapi2
from hashtag import Hashtag
from flask import current_app as app
from _sqlite3 import Row

class Hashtags:
    def __init__(self):
            self.last_hashtag_id = None

    def add_hashtag(self, hashtag):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""INSERT INTO HASHTAGS (NAME) VALUES (%s)"""
            cursor.execute(statement, (hashtag.name,))
            connection.commit()

    def delete_hashtag(self, hashtag_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""DELETE FROM HASHTAGCONTENTS WHERE (HASHTAGID = (%s))"""
            cursor.execute(statement, (hashtag_id,))
            connection.commit()
            statement ="""DELETE FROM HASHTAGS WHERE (ID = (%s))"""
            cursor.execute(statement, (hashtag_id,))
            connection.commit()
            cursor.close()

    def update_hashtag(self, hashtag_id, newHashtag):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""UPDATE HASHTAGS SET NAME = (%s) WHERE (ID = (%s))"""
            cursor.execute(statement, (newHashtag, hashtag_id))
            connection.commit()
            cursor.close()

    def get_hashtag(self, name):
         with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT ID FROM HASHTAGS WHERE (NAME = (%s))"""
            cursor.execute(statement, (name,))
            hashtag_id = cursor.fetchone()
            connection.commit()
            cursor.close()
            return hashtag_id

    def get_hashtagName(self, hashtag_id):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT NAME FROM HASHTAGS WHERE (ID = (%s))"""
            cursor.execute(statement, (hashtag_id, ))
            hashtagName = cursor.fetchone()
            connection.commit()
            cursor.close()
            return hashtagName

    def get_hashtags(self):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT ID, NAME FROM HASHTAGS ORDER BY ID"""
            cursor.execute(statement)
            hashtagTable = [(id, Hashtag(name))
                      for id, name in cursor]
            connection.commit()
            cursor.close()
            return hashtagTable

    def get_hashtagObj(self, hashtag_name):
            hashtag = Hashtag(hashtag_name)
            return hashtag
