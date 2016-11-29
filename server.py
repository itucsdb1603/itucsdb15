import datetime
import os
import json
import re
import psycopg2 as dbapi2

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from handlers import site
from flask.helpers import url_for
from moderatorlist import ModeratorList
from hashtags import Hashtags
from event import Event
from eventlist import EventList
from place import Place
from placelist import PlaceList

def create_app():
    app = Flask(__name__)
    app.register_blueprint(site)
    app.moderatorlist = ModeratorList()
    app.hashtags = Hashtags()
    app.eventlist = EventList()
    app.placelist = PlaceList()
    return app
app = create_app()

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@app.route('/initevents')
def init_events_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """DROP TABLE IF EXISTS EVENTS"""
        cursor.execute(query)

        query = """CREATE TABLE EVENTS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(300),
        EVENT_DATE DATE,
        AREA_ID INTEGER,
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """ALTER TABLE EVENTS
        ADD FOREIGN KEY(AREA_ID)
        REFERENCES PLACES(AREA_ID)
        ON DELETE CASCADE"""
        cursor.execute(query)
        
        query = """INSERT INTO EVENTS (CONTENT, EVENT_DATE, AREA_ID) VALUES ('Holi Festival', '20161030', 1)"""
        cursor.execute(query)
        
        connection.commit()
        return redirect(url_for('site.home_page'))
    
@app.route('/initplaces')
def init_places_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS PLACES CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE PLACES (
        AREA_ID SERIAL,
        AREA VARCHAR(300),
        PRIMARY KEY(AREA_ID)
        )"""
        cursor.execute(query)

        query = """INSERT INTO PLACES (AREA) VALUES ('New Delhi')"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))

@app.route('/announcements',  methods=['GET', 'POST'])
def announcements_page():
    if 'add_announcement' in request.form:
        content = str(request.form['CONTENT'])
        area_id = str(request.form['AREA_ID'])

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""INSERT INTO ANNOUNCEMENTS (CONTENT, AREA_ID) VALUES (%s, %s)""", [content, area_id])

            connection.commit()

    elif 'init_announcements' in request.form:
        init_announcements_db()

    elif 'delete_announcement' in request.form:
        delete_id = request.form['delete_id']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""DELETE FROM ANNOUNCEMENTS WHERE ID=%s""", delete_id)

            connection.commit()

    elif 'edit_announcement' in request.form:
        edit_id = request.form['edit_id']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""SELECT * FROM ANNOUNCEMENTS WHERE ID=%s""", edit_id)
            selectedAnnouncement = cursor.fetchall()
            connection.commit()

            return render_template('update_announcement.html', announcements = selectedAnnouncement)

    elif 'selected_announcement_update' in request.form:
        announcement_id = request.form['id']
        announcement_content = request.form['content']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""UPDATE ANNOUNCEMENTS SET CONTENT=%s WHERE id=%s""", (announcement_content, announcement_id))
            connection.commit()

    allAnnouncements = get_announcements()
    allPlaces = get_places()
    return render_template('announcements.html', announcements = allAnnouncements, places = allPlaces)

def get_announcements():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT ID, CONTENT, AREA FROM ANNOUNCEMENTS JOIN PLACES ON (ANNOUNCEMENTS.AREA_ID = PLACES.AREA_ID)")
        announcements = cursor.fetchall()

        connection.commit()

        return announcements

def get_places():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PLACES")
        places = cursor.fetchall()

        connection.commit()

        return places


@app.route('/init_announcements')
def init_announcements_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS ANNOUNCEMENTS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE ANNOUNCEMENTS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(300),
        AREA_ID SERIAL,
        PRIMARY KEY(ID),
        FOREIGN KEY(AREA_ID) REFERENCES PLACES(AREA_ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )"""
        cursor.execute(query)

        query = """INSERT INTO ANNOUNCEMENTS (CONTENT, AREA_ID) VALUES ('Sample announcement!', 1)"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))
    
@app.route('/init_hashtags')
def init_hashtag_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS HASHTAGS"""
        cursor.execute(query)

        query = """CREATE TABLE HASHTAGS (
        ID SERIAL NOT NULL,
        NAME VARCHAR(50),
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """INSERT INTO HASHTAGS (NAME) VALUES ('#BazenHayat')"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))
    
@app.route('/init_users')
def init_user_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """DROP TABLE IF EXISTS USERS"""
        cursor.execute(query)
        
        query = """CREATE TABLE USERS(
        ID SERIAL NOT NULL,
        USERNAME VARCHAR(30),
        PASSWORD VARCHAR(15),
        MAIL_ID INTEGER,
        ENTRY_ID INTEGER,
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)
        
        query = """ALTER TABLE USERS
        ADD FOREIGN KEY(MAIL_ID)
        REFERENCES MAILS(MAIL_ID)
        ON DELETE CASCADE,
        ADD FOREIGN KEY(ENTRY_ID)
        REFERENCES ENTRIES(ENTRY_ID)
        ON DELETE CASCADE"""
        cursor.execute(query)
        
        query = """INSERT INTO USERS (USERNAME,PASSWORD) VALUES ('EXAMPLE USER','123456')"""
        cursor.execute(query)
        
        connection.commit()
        return redirect(url_for('site.home_page'))

@app.route('/init_mails')
def init_mails_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS MAILS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE MAILS (
        MAIL_ID SERIAL,
        EMAIL VARCHAR(100),
        PRIMARY KEY(MAIL_ID)
        )"""
        cursor.execute(query)

        query = """INSERT INTO MAILS (EMAIL) VALUES ('example@example.com')"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))
    
@app.route('/init_entries')
def init_entries_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        
        query = """DROP TABLE IF EXISTS ENTRIES CASCADE"""
        cursor.execute(query)
        
        query = """CREATE TABLE ENTRIES(
        ENTRY_ID SERIAL,
        ENTRY VARCHAR(300),
        PRIMARY KEY(ENTRY_ID)
        )"""
        cursor.execute(query)
        
        query = """INSERT INTO ENTRIES (ENTRY) VALUES ('This is an entry')"""
        cursor.execute(query)
        
        connection.commit()
        return redirect(url_for('site.home_page'))

@app.route('/init_topics')
def init_topics_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        
        query = """DROP TABLE IF EXISTS TOPICS CASCADE"""
        cursor.execute(query)
        
        query = """CREATE TABLE TOPICS(
        TOPIC_ID SERIAL,
        TOPIC VARCHAR(40),
        ENTRY_ID INTEGER,
        PRIMARY KEY(TOPIC_ID)
        )"""
        cursor.execute(query)
        
        query = """ALTER TABLE TOPICS
        ADD FOREIGN KEY(ENTRY_ID)
        REFERENCES ENTRIES(ENTRY_ID)
        ON DELETE CASCADE"""
        cursor.execute(query)
        
        query = """INSERT INTO TOPICS (TOPIC) VALUES ('EXAMPLE TOPIC')"""
        cursor.execute(query)
        
        connection.commit()
        return redirect(url_for('site.home_page'))
        
if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""
    app.run(host='0.0.0.0', port=port, debug=debug)
