import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app, request
from place import Place
from placelist import PlaceList
from flask import current_app as app
from _sqlite3 import Row

places = Blueprint('places', __name__)

@places.route('/places', methods = ['GET', 'POST'])
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
            return redirect(url_for('places.places_page', place_id=place._id))


@places.route('/places/delete', methods=['GET', 'POST'])
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
            return redirect(url_for('places.places_page'), place_id=place._id)

@places.route('/places/update', methods=['GET', 'POST'])
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
            return redirect(url_for('places.places_page'), place_id=place._id)
        
def get_places():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PLACES")
        places = cursor.fetchall()

        connection.commit()

        return places
    
@places.route('/initplaces')
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
        connection.commit()
        return redirect(url_for('site.home_page'))
