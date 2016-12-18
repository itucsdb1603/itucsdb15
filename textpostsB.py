import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import current_app, request
from textpost import TextPost
from textpostlist import TextPostList
from moderatorlist import ModeratorList
from flask import current_app as app
from _sqlite3 import Row
from flask_login import UserMixin, login_required, current_user, login_user
from flask_login.utils import login_required
from flask_login import logout_user

TextPosts = Blueprint('TextPosts', __name__)

@TextPosts.route('/textposts')
@login_required
def textposts_page():
    writer = app.moderatorlist.get_moderator(current_user.nickname)
    textposts = app.textpostlist.get_TextPostListofMod(writer)
    #return redirect(url_for('TextPosts.textposts_page'))
    return render_template('textposts.html', textposts=textposts)

@TextPosts.route('/textposts/add_text_posts', methods=['GET', 'POST'])
@login_required
def textpost_add_page():
    if request.method == 'GET':
        return render_template('textpost_add.html')
    else:
        content = str(request.form['content'])
        writer = app.moderatorlist.get_moderator(current_user.nickname)
        textPost = TextPost(content, writer)
        current_app.textpostlist.add_TextPost(textPost)
        return redirect(url_for('TextPosts.textposts_page'))

@TextPosts.route('/textposts/textpost_remove', methods=['GET', 'POST'])
@login_required
def textpost_remove_page():
    if request.method == 'GET':
        return render_template('textpost_remove.html')
    else:
        content = str(request.form['content'])
        postid = current_app.textpostlist.get_TextPost(content)
        current_app.textpostlist.delete_TextPost(postid)
        return redirect(url_for('TextPosts.textposts_page'))



@TextPosts.route('/textposts/textpost_update', methods=['GET', 'POST'])
@login_required
def textpost_update_page():
    if request.method == 'GET':
        return render_template('textpost_update.html')
    else:
        content = str(request.form['content'])
        new_content = str(request.form['new_content'])
        postid = current_app.textpostlist.get_TextPost(content) 
        current_app.textpostlist.update_TextPost(postid, new_content)
        return redirect(url_for('TextPosts.textposts_page'))

