import psycopg2 as dbapi2
from topic import Topic
from flask import current_app as app
from flask_login import UserMixin
from _sqlite3 import Row

class TopicList:
    def __init__(self):
            self.last_key = None

    def add_topic(self, topic):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO TOPICS (CONTENT, WRITER) VALUES (%s, %s)"""
                cursor.execute(query, (topic.content, topic.writer))
                connection.commit()

    def delete_topic(self, topic_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""DELETE FROM TOPICS WHERE (TOP_ID = (%s))"""
                cursor.execute(statement, (topic_id,))
                connection.commit()

    def get_topic(self, content):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT TOP_ID FROM TOPICS WHERE (CONTENT = (%s))"""
                cursor.execute(query, (content, ))
                topic_id = cursor.fetchone()  
                connection.commit()
            return topic_id

    def get_TopicList(self):
            with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               query = """SELECT TOP_ID, CONTENT, WRITER, NICKNAME FROM TOPICS JOIN
                MODERATORS ON WRITER=ID
                ORDER BY TOP_ID"""
               cursor.execute(query)
               topicTable = [(id, Topic(content, writer), modname)
                          for id, content, writer, modname in cursor]
            return topicTable
        
    def get_TopicListofMod(self, writer):
            with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               query = """SELECT TOP_ID, CONTENT, WRITER, NICKNAME FROM TOPICS JOIN
                MODERATORS ON WRITER=ID
                WHERE WRITER = (%s)
                ORDER BY TOP_ID"""
               cursor.execute(query, (writer,))
               topicTableofMod = [(id, Topic(content, writer), modname)
                          for id, content, writer, modname in cursor]
            return topicTableofMod