import psycopg2 as dbapi2
from imgpost import ImgPost
from flask import current_app as app
from flask_login import UserMixin
from _sqlite3 import Row

class ImgPostList:
    def __init__(self):
            self.last_key = None

    def add_imgPost(self, imgPost):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO IMGPOSTS (IMGNAME, MODID) VALUES (%s, %s)"""
                cursor.execute(query, (imgPost.imgname, imgPost.modid))
                connection.commit()

    def delete_imgPost(self, imgPost_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                #toBeDeleted = ImgPostList.get_imgPost(imgPost_id)
                #for row in cursor:
                #    id, nickname = row
                statement ="""DELETE FROM IMGPOSTS WHERE (IMGID = (%s))"""
                cursor.execute(statement, (imgPost_id,))
                connection.commit()

    def update_imgPost(self, imgPost_id, newName):
        with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""UPDATE IMGPOSTS
                SET IMGNAME = (%s)
                WHERE (IMGID = (%s))"""
                cursor.execute(statement, (newName, imgPost_id))
                connection.commit()

# get_imgPost is problematic!
    def get_imgPost(self, imgName):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT IMGID FROM IMGPOSTS WHERE (IMGNAME = (%s))"""
                cursor.execute(query, (imgName, ))
                imgid = cursor.fetchone()  # the possibility of having two or more images with the same name!!!
                #imgid, imgname, modid
                connection.commit()
            return imgid

    def get_imgPostList(self):
            #modid = app.get_moderator(current_user.nickname)
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT IMGID, IMGNAME, MODID, NICKNAME FROM IMGPOSTS JOIN
                MODERATORS ON MODID=ID
                ORDER BY IMGID"""
                cursor.execute(query)
                imgPostTable = [(id, ImgPost(imgname, modid), modname)
                          for id, imgname, modid, modname in cursor]
            return imgPostTable