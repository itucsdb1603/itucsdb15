from flask import Blueprint, render_template

from datetime import datetime
from flask import current_app, request
from moderator import Moderator
from moderatorlist import ModeratorList
from hashtag import Hashtag
from hashtags import Hashtags

site = Blueprint('site', __name__)

@site.route('/')
def home_page():
    now = datetime.now()
    day = now.strftime('%A')
    return render_template('home.html', day_name=day)

@site.route('/events')
def events_page():
    return render_template('events.html')

@site.route('/signup')
def signup_page():
    return render_template('signup.html')

@site.route('/announcements')
def announcements_page():
    return render_template('announcements.html')

@site.route('/hashtags')
def hashtags_page():
    hashtags = current_app.hashtags.get_hashtags()
    return render_template('hashtags.html', hashtags = hashtags.items())

@site.route('/hashtag/<int:hashtag_id>')
def hashtag_page(hashtag_id):
    hashtag = current_app.hashtags.get_hashtag(hashtag_id)
    return render_template('hashtag.html', hashtag=hashtag)

@site.route('/hashtags/add', methods=['GET', 'POST'])
def hashtag_add_page():
    if request.method == 'GET':
        return render_template('hashtag_add.html')
    else:
        name = request.form['name']
        hashtag = Hashtag(name)
        current_app.hashtags.add_hashtag(hashtag)
        return redirect(url_for('site.hashtag_page', hashtag_id=hashtag._id))

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
        nickname = request.form['nickname']
        password = request.form['password']
        moderator = Moderator(nickname, password)
        current_app.moderatorlist.add_moderator(moderator)
        return redirect(url_for('site.moderator_page', mod_id=moderator._id))

