import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import current_app, request
from topic import Topic
from topiclist import TopicList
from moderatorlist import ModeratorList
from flask import current_app as app
from _sqlite3 import Row
from flask_login import UserMixin, login_required, current_user, login_user
from flask_login.utils import login_required
from flask_login import logout_user

Topics = Blueprint('Topics', __name__)

@Topics.route('/topics')
@login_required
def topics_page():
    writer = app.moderatorlist.get_moderator(current_user.nickname)
    topics = app.topiclist.get_TopicListofMod(writer)
    return render_template('topics.html', topics=topics)

@Topics.route('/topics/add_topics', methods=['GET', 'POST'])
@login_required
def topic_add_page():
    if request.method == 'GET':
        return render_template('topic_add.html')
    else:
        content = str(request.form['content'])
        writer = app.moderatorlist.get_moderator(current_user.nickname)
        topic = Topic(content, writer)
        current_app.topiclist.add_topic(topic)
        return redirect(url_for('Topics.topics_page'))

@Topics.route('/topics/topics_delete', methods=['GET', 'POST'])
@login_required
def topic_remove_page():
    if request.method == 'GET':
        return render_template('topic_delete.html')
    else:
        content = str(request.form['content'])
        topic_id = current_app.topiclist.get_topic(content)
        current_app.topiclist.delete_topic(topic_id)
        return redirect(url_for('Topics.topics_page'))






