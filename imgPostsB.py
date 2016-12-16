import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import current_app, request
from imgpost import ImgPost
from imgpostlist import ImgPostList
from flask import current_app as app
from _sqlite3 import Row

imgPosts = Blueprint('imgPosts', __name__)

@imgPosts.route('/moderator/success')
def success_page():
    return render_template('success.html')

@imgPosts.route('/moderators/add_image_posts', methods=['GET', 'POST'])
def imgpost_add_page():
    if request.method == 'GET':
        return render_template('imgpost_add.html')
    else:
        imgname = str(request.form['imgname'])
        modid = int(request.form['modid'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            statement ="""INSERT INTO IMGPOSTS (IMGNAME, MODID) VALUES (%s, %s)"""
            cursor.execute(statement, (imgname, modid))
            connection.commit()

            imgPost = ImgPost(imgname, modid)

            current_app.imgpostlist.add_imgPost(imgPost)
            return redirect(url_for('imgPosts.success_page'))



@imgPosts.route('/moderators/imgpost_remove', methods=['GET', 'POST'])
def imgpost_remove_page():
    if request.method == 'GET':
        return render_template('imgpost_remove.html')
    else:
        imgname = str(request.form['imgname'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""SELECT IMGID, IMGNAME FROM IMGPOSTS WHERE (IMGNAME = (%s))"""
            cursor.execute(statement, (imgname,))
            connection.commit()
            for row in cursor:
                id, nickname = row
            statement ="""DELETE FROM IMGPOSTS WHERE (IMGID = (%s))"""
            cursor.execute(statement, (id,))
            connection.commit()
            current_app.imgpostlist.delete_imgPost(id)
            return redirect(url_for('mods.moderators_page'))



@imgPosts.route('/moderators/imgpost_update', methods=['GET', 'POST'])
def imgpost_update_page():
    if request.method == 'GET':
        return render_template('imgpost_update.html')
    else:
        imgname = str(request.form['imgname'])
        newimgname = str(request.form['newimgname'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE IMGPOSTS
            SET IMGNAME = (%s)
            WHERE (IMGNAME = (%s))"""
            cursor.execute(statement, (newimgname, imgname))
            connection.commit()

            cursor = connection.cursor()
            statement = """SELECT IMGID, IMGNAME FROM IMGPOSTS WHERE (IMGNAME = (%s))"""
            cursor.execute(statement, (newimgname,))
            connection.commit()
            for row in cursor:
                id, nickname = row
            postToUpdate = current_app.imgpostlist.get_imgPost(id)
            postToUpdate.change_nickname(newimgname)
            return redirect(url_for('mods.moderators_page'))

