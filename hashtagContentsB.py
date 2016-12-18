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
from flask import current_app as app
from _sqlite3 import Row

hashtagContents = Blueprint('hashtagContents', __name__)

@hashtagContents.route('/hashtag/addContent/<hashtag_id>', methods=['GET', 'POST'])
def hashtagContent_add_page(hashtag_id):
    if request.method == 'GET':
        return render_template('hashtagContent_add.html')
    else:
        content = str(request.form['content'])
        hashtag_content = HashtagContent(content, hashtag_id)
        current_app.hashtagContents.add_content(hashtag_content)
        return redirect(url_for('hashtags.hashtag_page', hashtag_id=hashtag_id))

@hashtagContents.route('/hashtag/updateContent/<hashtag_id>', methods=['GET', 'POST'])
def hashtagContent_update_page(hashtag_id):
    if request.method == 'GET':
        return render_template('hashtagContent_update.html')
    else:
        contentid = str(request.form['id'])
        newContent = str(request.form['newContent'])
        current_app.hashtagContents.update_content(hashtag_id, contentid, newContent)
        return redirect(url_for('hashtags.hashtag_page', hashtag_id=hashtag_id))

@hashtagContents.route('/hashtag/deleteContent/<hashtag_id>', methods=['GET', 'POST'])
def hashtagContent_delete_page(hashtag_id):
    if request.method == 'GET':
        return render_template('hashtagContent_delete.html')
    else:
        contentid = str(request.form['id'])
        current_app.hashtagContents.delete_content(hashtag_id, contentid)
        return redirect(url_for('hashtags.hashtag_page', hashtag_id=hashtag_id))