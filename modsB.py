import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template, flash, abort
from flask import redirect
from flask.helpers import url_for
from flask import current_app, request
from moderator import Moderator
from moderatorlist import ModeratorList
from flask import current_app as app
from _sqlite3 import Row
from flask_login import UserMixin, login_required, current_user, login_user
from flask_login.utils import login_required
from flask_login import logout_user
from passlib.apps import custom_app_context as pwd_context

mods = Blueprint('mods', __name__)

@mods.route('/moderators')
@login_required
def moderators_page():
    moderators = current_app.moderatorlist.get_moderators()
    return render_template('moderators.html', moderators=moderators)

@mods.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    moderators = current_app.moderatorlist.get_moderators()
    return render_template('profile.html', moderators=moderators)

@mods.route('/moderators/add', methods=['GET', 'POST'])
@login_required
def mod_add_page():
    if not current_user.nickname == 'admin':
        abort(401)
    if request.method == 'GET':
        return render_template('modedit.html')
    else:
        nickname = str(request.form['nickname'])
        password = str(request.form['password'])
        hashed = pwd_context.encrypt(password)
        moderator = Moderator(nickname, hashed)
        current_app.moderatorlist.add_moderator(moderator)
        modid = current_app.moderatorlist.get_moderator(moderator.nickname)
        message = 'Moderator is added.'
        return redirect(url_for('mods.moderators_page'))

@mods.route('/profile/remove', methods=['GET', 'POST'])
@login_required
def mod_remove_page():
    if not current_user.nickname == 'admin':
        abort(401)
    if request.method == 'GET':
        return render_template('modremove.html')
    else:
        nickname = str(request.form['nickname'])
        mod_id = current_app.moderatorlist.get_moderator(nickname)
        current_app.moderatorlist.delete_moderator(mod_id)
        message = 'You have deleted your account.'
        return redirect(url_for('mods.moderators_page'))

@mods.route('/moderators/update', methods=['GET', 'POST'])
@login_required
def mod_update_page():
    if not current_user.nickname == 'admin':
        abort(401)
    if request.method == 'GET':
        return render_template('modupdate.html')
    else:
        nickname = str(request.form['nickname'])
        newnickname = str(request.form['newnickname'])
        mod_id = current_app.moderatorlist.get_moderator(nickname)
        current_app.moderatorlist.update_moderator(mod_id, newnickname)
        #message = 'You have changed your name.'
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
        NICKNAME VARCHAR(20) UNIQUE NOT NULL,
        PASSWORD VARCHAR(300) NOT NULL,
        IS_ADMIN VARCHAR(6),
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
        #flash('Moderators db is initialized.')
        return redirect(url_for('site.signup_page'))
