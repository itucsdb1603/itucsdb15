import os
import json
import re
import psycopg2 as dbapi2

from flask import Blueprint, render_template
from flask import redirect
from flask.helpers import url_for
from datetime import datetime
from flask import current_app, request
from imgpost import ImgPost
from imgpostlist import ImgPostList
from moderatorlist import ModeratorList
from flask import current_app as app
from _sqlite3 import Row
from flask_login import UserMixin, login_required, current_user, login_user
from flask_login.utils import login_required
from flask_login import logout_user

imgPosts = Blueprint('imgPosts', __name__)

@imgPosts.route('/imageposts')
@login_required
def imgposts_page():
    imgposts = app.imgpostlist.get_imgPostList()
    return render_template('imgposts.html', imgposts=imgposts)

@imgPosts.route('/imageposts/add_image_posts', methods=['GET', 'POST'])
@login_required
def imgpost_add_page():
    if request.method == 'GET':
        return render_template('imgpost_add.html')
    else:
        imgname = str(request.form['imgname'])
        modid = app.moderatorlist.get_moderator(current_user.nickname)
        imgPost = ImgPost(imgname, modid)
        current_app.imgpostlist.add_imgPost(imgPost)
        return redirect(url_for('imgPosts.imgposts_page'))

@imgPosts.route('/imageposts/imgpost_remove', methods=['GET', 'POST'])
@login_required
def imgpost_remove_page():
    if request.method == 'GET':
        return render_template('imgpost_remove.html')
    else:
        imgname = str(request.form['imgname'])
        imgid = current_app.imgpostlist.get_imgPost(imgname)
        current_app.imgpostlist.delete_imgPost(imgid)
        return redirect(url_for('imgPosts.imgposts_page'))



@imgPosts.route('/imageposts/imgpost_update', methods=['GET', 'POST'])
@login_required
def imgpost_update_page():
    if request.method == 'GET':
        return render_template('imgpost_update.html')
    else:
        imgname = str(request.form['imgname'])
        newimgname = str(request.form['newimgname'])
        imgid = current_app.imgpostlist.get_imgPost(imgname) # to be updated
        current_app.imgpostlist.update_imgPost(imgid, newimgname)
        return redirect(url_for('imgPosts.imgposts_page'))

