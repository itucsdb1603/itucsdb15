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
from textpost import TextPost
from textpostlist import TextPostList
from flask import current_app as app
from sqlite3 import Row
from flask_login import LoginManager, current_user, login_user, logout_user
from passlib.apps import custom_app_context as pwd_context

site = Blueprint('site', __name__)


@site.route('/home')
def home_page():
    message = 'You have successfully logged in'
    return render_template('home.html', message=message)

#---- Login ----

@site.route('/', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        nickname = str(request.form['nickname'])
        password = str(request.form['password'])
        hashed = pwd_context.encrypt(password)
        moderator = Moderator(nickname, hashed)
        app.moderatorlist.add_moderator(moderator)
        modid = app.moderatorlist.get_moderator(nickname)

        login_user(moderator)
        return redirect(url_for('site.home_page'))

@site.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        nickname = str(request.form['nickname'])
        mod = app.moderatorlist.get_moderatorObj(nickname)
        if mod is not None:
                password = str(request.form['password'])
                if pwd_context.verify(password, mod.password):
                    login_user(mod)
                    message = 'You have logged in.'
                    next_page = request.args.get('next', url_for('site.home_page'))
                    return redirect(next_page)
                else:
                    message = 'Invalid credentials.'
                    return render_template('login.html', message=message)
        else:
            message = 'Invalid credentials.'
            return render_template('login.html', message=message)

@site.route('/logout')
def logout_page():
    logout_user()
    message = 'You have logged out.'
    return render_template('logout.html', message=message)

#---- Login end ----





