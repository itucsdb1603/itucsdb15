import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import current_app, request
from moderator import Moderator
from moderatorlist import ModeratorList
from hashtag import Hashtag
from hashtags import Hashtags
from event import Event
from eventlist import EventList
from place import Place
from placelist import PlaceList
from flask import current_app as app
from _sqlite3 import Row

site = Blueprint('site', __name__)


@site.route('/')
def home_page():
    now = datetime.now()
    day = now.strftime('%A')
    return render_template('home.html', day_name=day)

@site.route('/events', methods = ['GET', 'POST'])
def events_page():
    if request.method == 'GET':
        events = current_app.eventlist.get_events()
        places = current_app.placelist.get_places()
        return render_template('events.html', events=sorted(events.items()), places=sorted(places.items()))
    else:
        content = str(request.form['content'])
        place = str(request.form['option'])
        event_date = str(request.form['event_date'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT AREA_ID, AREA FROM PLACES WHERE (AREA=(%s))"""
            cursor.execute(statement, (place,))
            connection.commit()
            for row in cursor:
                area_id, place = row
            statement ="""INSERT INTO EVENTS (CONTENT, EVENT_DATE, AREA_ID) VALUES (%s, %s, %s)"""
            cursor.execute(statement, (content, event_date, area_id,))
            connection.commit()

            event = Event(content, event_date)

            current_app.eventlist.add_event(event)
            return redirect(url_for('site.events_page', event_id=event._id))


@site.route('/events/delete', methods=['GET', 'POST'])
def delete_event():
    if request.method == 'GET':
        return render_template('delete_event.html')
    else:
        content = str(request.form['content'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""SELECT ID, CONTENT FROM EVENTS WHERE (CONTENT = (%s))"""
            cursor.execute(statement, (content,))
            connection.commit()
            for row in cursor:
                id, content = row
            statement ="""DELETE FROM EVENTS WHERE (ID = (%s))"""
            cursor.execute(statement, (id,))
            connection.commit()
            current_app.eventlist.delete_event(id)
            return redirect(url_for('site.events_page'))
        
@site.route('/places', methods = ['GET', 'POST'])
def places_page():
    if request.method == 'GET':
        places = current_app.placelist.get_places()
        return render_template('places.html', places=sorted(places.items()))
    else:
        area = str(request.form['area'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            statement ="""INSERT INTO PLACES (AREA) VALUES (%s)"""
            cursor.execute(statement, [area])
            connection.commit()

            place = Place(area)

            current_app.placelist.add_place(place)
            return redirect(url_for('site.places_page', place_id=place._id))


@site.route('/places/delete', methods=['GET', 'POST'])
def delete_place():
    if request.method == 'GET':
        return render_template('delete_place.html')
    else:
        area = str(request.form['area'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""SELECT AREA_ID, AREA FROM PLACES WHERE (AREA = (%s))"""
            cursor.execute(statement, (area,))
            connection.commit()
            for row in cursor:
                id, area = row
            statement ="""DELETE FROM PLACES WHERE (AREA_ID = (%s))"""
            cursor.execute(statement, (id,))
            connection.commit()
            current_app.placelist.delete_place(id)
            return redirect(url_for('site.places_page'))

        
@site.route('/signup')
def signup_page():
    return render_template('signup.html')

@site.route('/hashtags')
def hashtags_page():
    hashtags = current_app.hashtags.get_hashtags()
    return render_template('hashtags.html', hashtags = sorted(hashtags.items()))

@site.route('/hashtag/<int:hashtag_id>')
def hashtag_page(hashtag_id):
    hashtag = current_app.hashtags.get_hashtag(hashtag_id)
    return render_template('hashtag.html', hashtag=hashtag)

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
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""SELECT ID FROM HASHTAGS WHERE (NAME = (%s))"""
            cursor.execute(statement, (name,))
            connection.commit()
            for row in cursor:
                id = row
            statement ="""DELETE FROM HASHTAGS WHERE (ID = (%s))"""
            cursor.execute(statement, (id,))
            connection.commit()
            current_app.hashtags.delete_hashtag(id)
            return redirect(url_for('site.hashtags_page'))

@site.route('/moderators')
def moderators_page():
    moderators = current_app.moderatorlist.get_moderators()
    return render_template('moderators.html', moderators=sorted(moderators.items()))

@site.route('/moderator/<int:mod_id>')
def moderator_page(mod_id):
    moderator = current_app.moderatorlist.get_moderator(mod_id)
    return render_template('moderator.html', moderator=moderator)

@site.route('/moderators/add', methods=['GET', 'POST'])
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
            return redirect(url_for('site.moderator_page', mod_id=moderator._id))

@site.route('/moderators/remove', methods=['GET', 'POST'])
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
            return redirect(url_for('site.moderators_page'))

@site.route('/moderators/update', methods=['GET', 'POST'])
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
            return redirect(url_for('site.moderators_page'))

@site.route('/initmods')
def init_mod_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
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

        connection.commit()
        return redirect(url_for('site.home_page'))
