import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app, request
from event import Event
from eventlist import EventList
from flask import current_app as app
from _sqlite3 import Row

events = Blueprint('events', __name__)

@events.route('/events', methods = ['GET', 'POST'])
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
            return redirect(url_for('events.events_page', event_id=event._id))


@events.route('/events/delete', methods=['GET', 'POST'])
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
            return redirect(url_for('events.events_page'))

@events.route('/events/update', methods = ['GET', 'POST'])
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
            return redirect(url_for('events.events_page'))

