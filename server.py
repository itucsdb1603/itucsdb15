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

def create_app():
    app = Flask(__name__)
    app.register_blueprint(site)
    app.moderatorlist = ModeratorList()
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

        query = """CREATE TABLE EVENTS (ID INTEGER, CONTENT VARCHAR(300), EVENT_DATE DATE)"""
        cursor.execute(query)

        query = """INSERT INTO EVENTS (ID, CONTENT, EVENT_DATE) VALUES (0, 'Holi Festival', '20161030')"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))


@app.route('/announcements',  methods=['GET', 'POST'])
def announcements_page():
    if 'add_announcement' in request.form:
        content = str(request.form['CONTENT'])

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            cursor.execute("""INSERT INTO ANNOUNCEMENTS (CONTENT) VALUES (%s)""", [content])

            connection.commit()

    elif 'init_announcements' in request.form:
        init_announcements_db()

    allAnnouncements = get_announcements()
    return render_template('announcements.html', announcements = allAnnouncements)

def get_announcements():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM ANNOUNCEMENTS")
        announcements = cursor.fetchall()

        connection.commit()

        return announcements


@app.route('/init_announcements')
def init_announcements_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS ANNOUNCEMENTS"""
        cursor.execute(query)

        query = """CREATE TABLE ANNOUNCEMENTS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(300),
        PRIMARY KEY(ID)
        )"""
        cursor.execute(query)

        query = """INSERT INTO ANNOUNCEMENTS (CONTENT) VALUES ('Sample announcement!')"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))


app.hashtags = Hashtags()

@app.route('/init_hashtags')
def init_hashtags_db():
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
