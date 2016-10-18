from flask import Blueprint, render_template

from datetime import datetime
from flask import current_app

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

<<<<<<< HEAD
@site.route('/hashtags')
def hashtags_page():
    return render_template('hashtags.html')
=======
@site.route('/moderators')
def moderators_page():
    return render_template('moderators.html')
>>>>>>> 8531941bfa739d2a234d5ff4022e8fbbbd0aa2a1
