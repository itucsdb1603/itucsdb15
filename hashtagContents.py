import psycopg2 as dbapi2
from hashtagContent import HashtagContent
from flask import current_app as app
from _sqlite3 import Row

class HashtagContents:
    def __init__(self):
        self.last_content_id = None

    def add_content(self, hashtagcontent):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""INSERT INTO HASHTAGCONTENTS (HASHTAGID, CONTENT) VALUES (%s, %s)"""
            cursor.execute(statement, (hashtagcontent.hashtagid, hashtagcontent.content))
            connection.commit()

    def delete_content(self, hashtagid, contentid):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""DELETE FROM HASHTAGCONTENTS WHERE (ID = (%s) AND HASHTAGID = (%s))"""
            cursor.execute(statement, (contentid, hashtagid))
            connection.commit()

    def update_content(self, hashtagid, content_id, newcontent):
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""UPDATE HASHTAGCONTENTS SET CONTENT = (%s) WHERE (ID = (%s) AND HASHTAGID = (%s))"""
            cursor.execute(statement, (newcontent, content_id, hashtagid))
            connection.commit()

    def get_contents(self, hashtagid):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT ID, HASHTAGID, CONTENT FROM HASHTAGCONTENTS WHERE HASHTAGID = (%s) ORDER BY ID"""
                cursor.execute(statement, (hashtagid,))
                contents = [(id, HashtagContent(hashtagid, content))
                          for id, hashtagid, content in cursor]
            return contents
