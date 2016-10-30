from flask import Blueprint, render_template

from datetime import datetime
from flask import current_app, request
from moderator import Moderator
from moderatorlist import ModeratorList

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
    return render_template('hashtags.html')

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

