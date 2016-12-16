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
    return render_template('moderators.html', moderators=sorted(moderators.items()))

@mods.route('/moderator/<int:mod_id>')
def moderator_page(mod_id):
    moderator = current_app.moderatorlist.get_moderator(mod_id)
    return render_template('moderator.html', moderator=moderator)

@mods.route('/moderators/add', methods=['GET', 'POST'])
def mod_add_page():
    if request.method == 'GET':
        return render_template('modedit.html')
    else:
        nickname = str(request.form['nickname'])
        password = str(request.form['password'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            statement ="""INSERT INTO MODERATORS (NICKNAME, PASSWORD) VALUES (%s, %s)"""
            cursor.execute(statement, (nickname, password))
            connection.commit()

            moderator = Moderator(nickname, password)

            current_app.moderatorlist.add_moderator(moderator)
            return redirect(url_for('mods.moderator_page', mod_id=moderator._id))

@mods.route('/moderators/remove', methods=['GET', 'POST'])
def mod_remove_page():
    if request.method == 'GET':
        return render_template('modremove.html')
    else:
        nickname = str(request.form['nickname'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""SELECT ID, NICKNAME FROM MODERATORS WHERE (NICKNAME = (%s))"""
            cursor.execute(statement, (nickname,))
            connection.commit()
            for row in cursor:
                id, nickname = row
            statement ="""DELETE FROM MODERATORS WHERE (ID = (%s))"""
            cursor.execute(statement, (id,))
            connection.commit()
            current_app.moderatorlist.delete_moderator(id)
            return redirect(url_for('mods.moderators_page'))

@mods.route('/moderators/update', methods=['GET', 'POST'])
def mod_update_page():
    if request.method == 'GET':
        return render_template('modupdate.html')
    else:
        nickname = str(request.form['nickname'])
        newnickname = str(request.form['newnickname'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE MODERATORS
            SET NICKNAME = (%s)
            WHERE (NICKNAME = (%s))"""
            cursor.execute(statement, (newnickname, nickname))
            connection.commit()

            cursor = connection.cursor()
            statement = """SELECT ID, NICKNAME FROM MODERATORS WHERE (NICKNAME = (%s))"""
            cursor.execute(statement, (newnickname,))
            connection.commit()
            for row in cursor:
                id, nickname = row
            moderatorToUpdate = current_app.moderatorlist.get_moderator(id)
            moderatorToUpdate.change_nickname(newnickname)
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
