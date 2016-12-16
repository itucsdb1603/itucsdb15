import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import current_app, request
from hashtag import Hashtag
from hashtags import Hashtags
from hashtagContent import HashtagContent
from hashtagContents import HashtagContents
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

            event = Event(content, event_date, place)

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

@site.route('/events/update', methods = ['GET', 'POST'])
def update_event():
    if request.method == 'GET':
        events = current_app.eventlist.get_events()
        places = current_app.placelist.get_places()
        return render_template('update_event.html', events=sorted(events.items()), places=sorted(places.items()))
    else:
        content = str(request.form['content'])
        new_content = str(request.form['new_content'])
        new_place = str(request.form['option'])
        new_date = str(request.form['new_date'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT AREA_ID, AREA FROM PLACES WHERE (AREA=(%s))"""
            cursor.execute(statement, (new_place,))
            connection.commit()
            for row in cursor:
                area_id, place = row

            cursor = connection.cursor()
            statement = """UPDATE EVENTS
            SET CONTENT = (%s),
            EVENT_DATE = (%s),
            AREA_ID = (%s)
            WHERE (CONTENT=(%s))"""
            cursor.execute(statement, (new_content, new_date, area_id, content))
            connection.commit()

            cursor = connection.cursor()
            statement = """SELECT ID, CONTENT FROM EVENTS WHERE (CONTENT = (%s))"""
            cursor.execute(statement, (new_content,))
            connection.commit()
            for row in cursor:
                id, content = row

            updated_event = current_app.eventlist.get_event(id)
            updated_event.update_event(new_content, new_place, new_date)
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
            return redirect(url_for('site.places_page'), place_id=place._id)

@site.route('/places/update', methods=['GET', 'POST'])
def update_place():
    if request.method == 'GET':
        return render_template('update_place.html')
    else:
        area= str(request.form['area'])
        new_area = str(request.form['new_area'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement ="""UPDATE PLACES
            SET AREA = (%s)
            WHERE AREA = (%s)"""
            cursor.execute(statement, (new_area, area,))
            connection.commit()

            cursor = connection.cursor()
            statement = """SELECT AREA_ID, AREA FROM PLACES WHERE (AREA = (%s))"""
            cursor.execute(statement, (new_area,))
            connection.commit()
            for row in cursor:
                area_id, area = row

            updated_place = current_app.placelist.get_place(area_id)
            updated_place.update_place(new_area)
            return redirect(url_for('site.places_page'), place_id=place._id)

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

