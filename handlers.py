import os
import json
import re
import psycopg2 as dbapi2

from flask import Flask, session, flash
from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import request
from moderator import Moderator
from moderatorlist import ModeratorList
from hashtag import Hashtag
from hashtags import Hashtags
from hashtagContent import HashtagContent
from hashtagContents import HashtagContents
from event import Event
from eventlist import EventList
from place import Place
from placelist import PlaceList
from flask import current_app as app
from sqlite3 import Row
from flask_login import LoginManager, current_user, login_user

site = Blueprint('site', __name__)


@site.route('/home')
def home_page():
    moderator = current_user._get_current_object()
    flash('You are successfully logged in')
    return render_template('home.html')

#---- Login ----

@site.route('/', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        nickname = str(request.form['nickname'])
        password = str(request.form['password'])
        secret = str(request.form['secret'])
        adminkey = 'admin'
        moderator = Moderator(nickname, password)
        app.moderatorlist.add_moderator(moderator)
        modid = app.moderatorlist.get_moderator(nickname)
        if secret == adminkey:
            moderator.is_admin = True
            print("The mod", moderator.nickname, " is admin")
        else:
            print("The mod", moderator.nickname, " is NOT admin")
        login_user(moderator)
        return redirect(url_for('site.home_page'))

@site.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == 'GET':
        return render_template('signin.html')
    else:
        nickname = str(request.form['nickname'])
        password = str(request.form['password'])

        return redirect(url_for('site.home_page'))

#---- Login end ----

@site.route('/hashtags')
def hashtags_page():
    hashtags = current_app.hashtags.get_hashtags()
    return render_template('hashtags.html', hashtags = sorted(hashtags.items()))

@site.route('/hashtag/<int:hashtag_id>')
def hashtag_page(hashtag_id):
    hashtag = current_app.hashtags.get_hashtag(hashtag_id)
    hashtagContents = hashtag.hashtagContents.get_contents()
    return render_template('hashtag.html', hashtag=hashtag, hashtagContents = sorted(hashtagContents.items()))

@site.route('/hashtags/add', methods=['GET', 'POST'])
def hashtag_add_page():
    if request.method == 'GET':
        return render_template('hashtag_add.html')
    else:
        name = str(request.form['name'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            statement ="""INSERT INTO HASHTAGS (NAME) VALUES (%s)"""
            cursor.execute(statement, (name,))
            connection.commit()

            hashtag = Hashtag(name)

            current_app.hashtags.add_hashtag(hashtag)
            return redirect(url_for('site.hashtag_page', hashtag_id=hashtag._id))

@site.route('/hashtags/update', methods=['GET', 'POST'])
def hashtag_update_page():
    if request.method == 'GET':
        return render_template('hashtag_update.html')
    else:
        name = str(request.form['name'])
        newhashtag = str(request.form['newhashtag'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE HASHTAGS
            SET NAME = (%s)
            WHERE (NAME = (%s))"""
            cursor.execute(statement, (newhashtag, name))
            connection.commit()

            cursor = connection.cursor()
            statement = """SELECT ID, NAME FROM HASHTAGS WHERE (NAME = (%s))"""
            cursor.execute(statement, (newhashtag,))
            connection.commit()
            for row in cursor:
                id, name = row
            hashtagToBeUpdated = current_app.hashtags.get_hashtag(id)
            hashtagToBeUpdated.update_name(newhashtag)
            return redirect(url_for('site.hashtags_page'))

@site.route('/hashtags/remove', methods=['GET', 'POST'])
def hashtag_delete_page():
    if request.method == 'GET':
        return render_template('hashtag_delete.html')
    else:
        name = str(request.form['name'])
        try:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""SELECT ID FROM HASHTAGS WHERE (NAME = (%s))"""
                cursor.execute(statement, (name,))
                connection.commit()
                for id in cursor:
                    statement ="""DELETE FROM HASHTAGS WHERE (ID = (%s))"""
                    cursor.execute(statement, (id,))
                    connection.commit()
                    current_app.hashtags.delete_hashtag(id)

        except dbapi2.DatabaseError:
            connection.rollback()
        finally:
            connection.close()

        return redirect(url_for('site.hashtags_page'))

@site.route('/hashtag/<int:hashtag_id>/add', methods=['GET', 'POST'])
def hashtagContent_add_page():
    if request.method == 'GET':
        return render_template('hashtagContent_add.html')
    else:
        content = str(request.form['content'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            statement ="""INSERT INTO HASHTAGCONTENTS (HASHTAGID, CONTENT) VALUES (%s, %s)"""
            cursor.execute(statement, (content, hashtag_id))
            connection.commit()

            hashtagContent = HashtagContent(content)
            hashtag = current_app.hashtags.get_hashtag(hashtag_id)
            current_app.hashtag.hashtagContents.add_content(hashtagContent)
            return redirect(url_for('site.hashtag_page', hashtag_id=hashtag._id))

@site.route('/hashtag/<int:hashtag_id>/update', methods=['GET', 'POST'])
def hashtagContent_update_page():
    if request.method == 'GET':
        return render_template('hashtagContent_update.html')
    else:
        contentid = str(request.form['id'])
        newContent = str(request.form['newContent'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE HASHTAGCONTENTS
            SET CONTENT = (%s)
            WHERE (ID = (%s) AND HASHTAGID = (%s))"""
            cursor.execute(statement, (newContent, contentid, hashtag_id))
            connection.commit()

            cursor = connection.cursor()
            statement = """SELECT ID, CONTENT FROM HASHTAGCONTENTS WHERE (ID = (%s) AND HASHTAGID = (%s))"""
            cursor.execute(statement, (contentid, hashtag_id))
            connection.commit()
            hashtag = current_app.hashtags.get_hashtag(hashtag_id)
            for row in cursor:
                id, content = row
                contentToBeUpdated = current_app.hashtag.hashtagContents.get_content(id)
                contentToBeUpdated.update_content(newContent)
            return redirect(url_for('site.hashtag_page', hashtag_id=hashtag._id))

@site.route('/hashtag/<int:hashtag_id>/remove', methods=['GET', 'POST'])
def hashtagContent_delete_page():
    if request.method == 'GET':
        return render_template('hashtagContent_delete.html')
    else:
        contentid = str(request.form['id'])
        try:
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""DELETE FROM HASHTAGCONTENTS WHERE (ID = (%s) AND HASHTAGID = (%s))"""
                cursor.execute(statement, (contentid, hashtag_id))
                connection.commit()
                hashtag = current_app.hashtags.get_hashtag(hashtag_id)
                current_app.hashtag.hashtagContents.delete_content(contentid)

        except dbapi2.DatabaseError:
            connection.rollback()
        finally:
            connection.close()
        return redirect(url_for('site.hashtag_page', hashtag_id=hashtag._id))

