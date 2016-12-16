import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app, request
from moderator import Moderator
from moderatorlist import ModeratorList
from flask import current_app as app
from _sqlite3 import Row

mods = Blueprint('mods', __name__)

@mods.route('/moderators')
def moderators_page():
    moderators = current_app.moderatorlist.get_moderators()
    return render_template('moderators.html', moderators=moderators)

@mods.route('/moderators/add', methods=['GET', 'POST'])
def mod_add_page():
    if request.method == 'GET':
        return render_template('modedit.html')
    else:
        nickname = str(request.form['nickname'])
        password = str(request.form['password'])
        moderator = Moderator(nickname, password)
        current_app.moderatorlist.add_moderator(moderator)
        modid = current_app.moderatorlist.get_moderator(moderator.nickname)
        return redirect(url_for('mods.moderators_page'))

@mods.route('/moderators/remove', methods=['GET', 'POST'])
def mod_remove_page():
    if request.method == 'GET':
        return render_template('modremove.html')
    else:
        nickname = str(request.form['nickname'])
        mod_id = current_app.moderatorlist.get_moderator(nickname)
        current_app.moderatorlist.delete_moderator(mod_id)
        return redirect(url_for('mods.moderators_page'))

@mods.route('/moderators/update', methods=['GET', 'POST'])
def mod_update_page():
    if request.method == 'GET':
        return render_template('modupdate.html')
    else:
        nickname = str(request.form['nickname'])
        newnickname = str(request.form['newnickname'])
        mod_id = current_app.moderatorlist.get_moderator(nickname)
        current_app.moderatorlist.update_moderator(mod_id, newnickname)
        return redirect(url_for('mods.moderators_page'))

@mods.route('/initmods')
def init_mod_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """DROP TABLE IF EXISTS IMGPOSTS"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS MODERATORS"""
        cursor.execute(query)

        query = """CREATE TABLE MODERATORS (
        ID SERIAL,
        NICKNAME VARCHAR(20) NOT NULL,
        PASSWORD VARCHAR(20),
        NATIONALITY VARCHAR(20),
        AGE INTEGER,
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """CREATE TABLE IMGPOSTS (
        IMGID SERIAL,
        IMGNAME VARCHAR(20),
        IMGTYPE VARCHAR(10),
        PRIMARY KEY(IMGID),
        MODID INTEGER,
        FOREIGN KEY (MODID) REFERENCES MODERATORS (ID)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
        )"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))
