import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app, request
from hashtag import Hashtag
from hashtags import Hashtags
from hashtagContent import HashtagContent
from hashtagContents import HashtagContents
from flask import current_app as app
from _sqlite3 import Row

hashtags = Blueprint('hashtags', __name__)

@hashtags.route('/hashtags')
def hashtags_page():
    hashtags = current_app.hashtags.get_hashtags()
    return render_template('hashtags.html', hashtags = hashtags)

@hashtags.route('/hashtag/<int:hashtag_id>')
def hashtag_page(hashtag_id):
    hashtag_name = current_app.hashtags.get_hashtagName(hashtag_id)
    hashtag = current_app.hashtags.get_hashtagObj(hashtag_name)
    hashtagContents = current_app.hashtagContents.get_contents(hashtag_id)
    return render_template('hashtag.html', hashtag=hashtag, hashtagContents = hashtagContents, hashtagid = hashtag_id)

@hashtags.route('/hashtags/add', methods=['GET', 'POST'])
def hashtag_add_page():
    if request.method == 'GET':
        return render_template('hashtag_add.html')
    else:
        name = str(request.form['name'])
        hashtag = Hashtag(name)
        current_app.hashtags.add_hashtag(hashtag)
        hashtag_id = current_app.hashtags.get_hashtag(hashtag.name)
        return redirect(url_for('hashtags.hashtags_page'))

@hashtags.route('/hashtags/update', methods=['GET', 'POST'])
def hashtag_update_page():
    if request.method == 'GET':
        return render_template('hashtag_update.html')
    else:
        name = str(request.form['name'])
        newhashtag = str(request.form['newhashtag'])
        hashtag_id = current_app.hashtags.get_hashtag(name)
        current_app.hashtags.update_hashtag(hashtag_id, newhashtag)
        return redirect(url_for('hashtags.hashtags_page'))

@hashtags.route('/hashtags/remove', methods=['GET', 'POST'])
def hashtag_delete_page():
    if request.method == 'GET':
        return render_template('hashtag_delete.html')
    else:
        name = str(request.form['name'])
        hashtag_id = current_app.hashtags.get_hashtag(name)
        current_app.hashtags.delete_hashtag(hashtag_id)
        return redirect(url_for('hashtags.hashtags_page'))

@hashtags.route('/init_hashtags')
def init_hashtag_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS HASHTAGCONTENTS"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS HASHTAGS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE HASHTAGS (
        ID SERIAL NOT NULL,
        NAME VARCHAR(50),
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """CREATE TABLE HASHTAGCONTENTS (
        ID SERIAL,
        HASHTAGID INTEGER,
        CONTENT VARCHAR(300),
        PRIMARY KEY(HASHTAGID, ID),
        FOREIGN KEY(HASHTAGID)
        REFERENCES HASHTAGS(ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
        )"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))