Parts Implemented by Mumtaz Cem Eris
====================================

**Tables**

There are two tables that are implemented by me. Tables can be seen from the '/initmods/' route which initializes 'MODERATORS'
and 'IMGPOSTS'. IMGPOSTS's MODID references MODERATORS's ID.

   .. code-block:: python

      @mods.route('/initmods')
      def init_mod_db():
          with dbapi2.connect(app.config['dsn']) as connection:
              cursor = connection.cursor()
              query = """DROP TABLE IF EXISTS IMGPOSTS"""
              cursor.execute(query)
              query = """DROP TABLE IF EXISTS MODERATORS"""
              cursor.execute(query)

              query = """CREATE TABLE MODERATORS (
              ID SERIAL,
              NICKNAME VARCHAR(20) UNIQUE NOT NULL,
              PASSWORD VARCHAR(300) NOT NULL,
              IS_ADMIN VARCHAR(6),
              PRIMARY KEY(ID)
              )"""
              cursor.execute(query)

              query = """CREATE TABLE IMGPOSTS (
              IMGID SERIAL,
              IMGNAME VARCHAR(20),
              IMGTYPE VARCHAR(10),
              PRIMARY KEY(IMGID),
              MODID INTEGER,
              FOREIGN KEY (MODID) REFERENCES MODERATORS (ID)
                  ON DELETE RESTRICT
                  ON UPDATE CASCADE
              )"""
              cursor.execute(query)

              connection.commit()
              #flash('Moderators db is initialized.')
              return redirect(url_for('site.signup_page'))


**Logins**

Starting from server.py, blueprints below and login manager are designed by me. It would be much clearer as you go further down.
Important note, users was going to be handled by Basar but since he left the project, users part is also implemented by me.
Moderators and users are merged after this situation
which means that every user is actually a moderator at the same time, users are all moderators and they will be called as moderators.

   .. code-block:: python

      login_manager = LoginManager()

      @login_manager.user_loader
      def load_user(user_id):
          mod = app.moderatorlist.get_moderatorObj(user_id)
          return mod

      def create_app():
          app = Flask(__name__)
          app.register_blueprint(site)
          app.register_blueprint(mods)
          app.register_blueprint(imgPosts)
          ...
          app.moderatorlist = ModeratorList()
          app.imgpostlist = ImgPostList()
          ...
          app.secret_key = "secret key"
          login_manager.init_app(app)
          login_manager.login_view = 'site.signup_page'
          return app


Continuing with the blueprint 'site', it has 4 significant routes which are '/home' home page, '/' the signup page, '/login' login page, and finally
'/logout' page. '/home' is the page that ShakeSpace welcomes the moderator who signed up before, and logged in. The other routes will be explained
one by one below.

   .. code-block:: python

      @site.route('/home')
      def home_page():
          message = 'You have successfully logged in'
          return render_template('home.html', message=message)

      #---- Login ----

      @site.route('/', methods=['GET', 'POST'])
      def signup_page():
          if request.method == 'GET':
              return render_template('signup.html')
          else:
              nickname = str(request.form['nickname'])
              password = str(request.form['password'])
              hashed = pwd_context.encrypt(password)
              moderator = Moderator(nickname, hashed)
              app.moderatorlist.add_moderator(moderator)
              modid = app.moderatorlist.get_moderator(nickname)

              login_user(moderator)
              return redirect(url_for('site.home_page'))

      @site.route('/login', methods=['GET', 'POST'])
      def login_page():
          if request.method == 'GET':
              return render_template('login.html')
          else:
              nickname = str(request.form['nickname'])
              mod = app.moderatorlist.get_moderatorObj(nickname)
              if mod is not None:
                      password = str(request.form['password'])
                      if pwd_context.verify(password, mod.password):
                          login_user(mod)
                          message = 'You have logged in.'
                          next_page = request.args.get('next', url_for('site.home_page'))
                          return redirect(next_page)
                      else:
                          message = 'Invalid credentials.'
                          return render_template('login.html', message=message)
              else:
                  message = 'Invalid credentials.'
                  return render_template('login.html', message=message)

      @site.route('/logout')
      def logout_page():
          logout_user()
          message = 'You have logged out.'
          return render_template('logout.html', message=message)

      #---- Login end ----

Route '/' is the signup page. That is the first page the visitor would see. When a visitor who has not logged in, will be redirected to this page.
In this route, nickname and password information is received from the visitor, the password will be hashed immediately and Moderator object will be
created. This object will be sent to add_moderator() function of moderatorlist, and with the given information the new moderator will be added to
the database by add_moderator(). After that, this moderator will be logged in, and the website redirects this moderator to the home page.


   .. code-block:: python

         @site.route('/', methods=['GET', 'POST'])
         def signup_page():
             if request.method == 'GET':
                 return render_template('signup.html')
             else:
                 nickname = str(request.form['nickname'])
                 password = str(request.form['password'])
                 hashed = pwd_context.encrypt(password)
                 moderator = Moderator(nickname, hashed)
                 app.moderatorlist.add_moderator(moderator)

                 login_user(moderator)
                 return redirect(url_for('site.home_page'))

Let's have a quick look at add_moderator. It gets the moderator object and inserts it into moderators table.

   .. code-block:: python

         def add_moderator(self, moderator):
                with dbapi2.connect(app.config['dsn']) as connection:
                        cursor = connection.cursor()
                        query = """INSERT INTO MODERATORS (NICKNAME, PASSWORD) VALUES (%s, %s)"""
                        cursor.execute(query, (moderator.nickname, moderator.password))
                        connection.commit()

Route '/login' is for the visitor who has an account already. login_page() would first get the nickname, and using get_moderatorObj(), the moderator
object 'mod' with given nickname would be returned. If there is no such 'mod' with given nickname, then 'mod' would be 'None'. If it is 'None' then
error message 'Invalid credentials.' will be returned to the user. If not, then the password would be checked. If it matches with the hashed password
in the database, then that moderator would be logged in. If the password is incorrect, same error message will be sent to the visitor.

   .. code-block:: python

      @site.route('/login', methods=['GET', 'POST'])
      def login_page():
          if request.method == 'GET':
              return render_template('login.html')
          else:
              nickname = str(request.form['nickname'])
              mod = app.moderatorlist.get_moderatorObj(nickname)
              if mod is not None:
                      password = str(request.form['password'])
                      if pwd_context.verify(password, mod.password):
                          login_user(mod)
                          message = 'You have logged in.'
                          next_page = request.args.get('next', url_for('site.home_page'))
                          return redirect(next_page)
                      else:
                          message = 'Invalid credentials.'
                          return render_template('login.html', message=message)
              else:
                  message = 'Invalid credentials.'
                  return render_template('login.html', message=message)

Route '/logout' is pretty straightforward, the current moderator would be logged out and redirected to the logout page with the message
below.

   .. code-block:: python

      @site.route('/logout')
      def logout_page():
          logout_user()
          message = 'You have logged out.'
          return render_template('logout.html', message=message)

**Admin**

There is only one admin in ShakeSpace, that is the moderator with the nickname of 'admin'. Admin can basically access to the 'moderators_page'
,namely the admin panel, in which the admin can add, remove or update moderators. It is a bit mentioned in 'User Manual' of my part with visual
materials. Here, the three methods add, delete, and update will be discussed.

   .. code-block:: python

      @mods.route('/moderators/add', methods=['GET', 'POST'])
      @login_required
      def mod_add_page():
          if not current_user.nickname == 'admin':
              abort(401)
          if request.method == 'GET':
              return render_template('modedit.html')
          else:
              nickname = str(request.form['nickname'])
              password = str(request.form['password'])
              hashed = pwd_context.encrypt(password)
              moderator = Moderator(nickname, hashed)
              current_app.moderatorlist.add_moderator(moderator)
              modid = current_app.moderatorlist.get_moderator(moderator.nickname)
              message = 'Moderator is added.'
              return redirect(url_for('mods.moderators_page'))

      @mods.route('/profile/remove', methods=['GET', 'POST'])
      @login_required
      def mod_remove_page():
          if not current_user.nickname == 'admin':
              abort(401)
          if request.method == 'GET':
              return render_template('modremove.html')
          else:
              nickname = str(request.form['nickname'])
              mod_id = current_app.moderatorlist.get_moderator(nickname)
              current_app.moderatorlist.delete_moderator(mod_id)
              message = 'You have deleted your account.'
              return redirect(url_for('mods.moderators_page'))

      @mods.route('/moderators/update', methods=['GET', 'POST'])
      @login_required
      def mod_update_page():
          if not current_user.nickname == 'admin':
              abort(401)
          if request.method == 'GET':
              return render_template('modupdate.html')
          else:
              nickname = str(request.form['nickname'])
              newnickname = str(request.form['newnickname'])
              mod_id = current_app.moderatorlist.get_moderator(nickname)
              current_app.moderatorlist.update_moderator(mod_id, newnickname)
              #message = 'You have changed your name.'
              return redirect(url_for('mods.moderators_page'))

Since there is only one admin and its nickname is 'admin', there is only one if condition to authorize the current user as admin, as seen below.
There is possibility of having 'abort(401)', although no moderators can see this page in the navigation bar. Admin can add a moderator just like
the moderator is added to the database in signup page with hashing.

   .. code-block:: python

      @mods.route('/moderators/add', methods=['GET', 'POST'])
      @login_required
      def mod_add_page():
          if not current_user.nickname == 'admin':
              abort(401)
          if request.method == 'GET':
              return render_template('modedit.html')
          else:
              nickname = str(request.form['nickname'])
              password = str(request.form['password'])
              hashed = pwd_context.encrypt(password)
              moderator = Moderator(nickname, hashed)
              current_app.moderatorlist.add_moderator(moderator)
              modid = current_app.moderatorlist.get_moderator(moderator.nickname)
              message = 'Moderator is added.'
              return redirect(url_for('mods.moderators_page'))

Admin can remove a moderator with typing its nickname. This function below would call get_moderator() which returns moderator id of the given nickname
of the moderator. Then it calls delete_moderator() with given id, and this function would find the corresponding moderator and deletes it from the
database. You can check 'Moderators' header for more detail about moderator functions.

   .. code-block:: python

      @mods.route('/profile/remove', methods=['GET', 'POST'])
      @login_required
      def mod_remove_page():
          if not current_user.nickname == 'admin':
              abort(401)
          if request.method == 'GET':
              return render_template('modremove.html')
          else:
              nickname = str(request.form['nickname'])
              mod_id = current_app.moderatorlist.get_moderator(nickname)
              current_app.moderatorlist.delete_moderator(mod_id)
              return redirect(url_for('mods.moderators_page'))

Finally, admin can update moderators' nicknames. The function gets the current and the new nickname. After having returned the moderator id, it
sends id and the new nickname to update_moderator() and this method updates the moderator in the database.

   .. code-block:: python

      @mods.route('/moderators/update', methods=['GET', 'POST'])
      @login_required
      def mod_update_page():
          if not current_user.nickname == 'admin':
              abort(401)
          if request.method == 'GET':
              return render_template('modupdate.html')
          else:
              nickname = str(request.form['nickname'])
              newnickname = str(request.form['newnickname'])
              mod_id = current_app.moderatorlist.get_moderator(nickname)
              current_app.moderatorlist.update_moderator(mod_id, newnickname)
              return redirect(url_for('mods.moderators_page'))

**Moderators**

It is crucial to know moderators since all users are treated as moderators. First, Moderator class will be examined. It uses features of
'UserMixin', and plus it has 'nickname' and 'password' variables.

   .. code-block:: python

      class Moderator(UserMixin):
          def __init__(self, nickname, password):
              self.nickname = nickname
              self.password = password
              self.active = True
              self.is_admin = False

          def get_id(self):
              return self.nickname

          @property
          def is_active(self):
              return self.active

Then ModeratorList class comes. This class has all the methods which are discussed in Logins part such as adding, deleting and updating. First,
add_moderator(self, moderator) will be examined. It gets a moderator object and inserts the nickname and the password (hashed) to the
table.

   .. code-block:: python

       def add_moderator(self, moderator):
           with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """INSERT INTO MODERATORS (NICKNAME, PASSWORD) VALUES (%s, %s)"""
                   cursor.execute(query, (moderator.nickname, moderator.password))
                   connection.commit()

delete_moderator(self, mod_id) gets id of the moderator, and first deletes the imageposts that have been posted by this moderator. Below,
'MODID' references 'ID' of the 'MODERATORS'. It is mentioned
in the user manual as well. Then it deletes the moderator using its id.

   .. code-block:: python

       def delete_moderator(self, mod_id):
           with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   statement ="""DELETE FROM IMGPOSTS WHERE (MODID = (%s))"""
                   cursor.execute(statement, (mod_id,))
                   connection.commit()
                   statement ="""DELETE FROM MODERATORS WHERE (ID = (%s))"""
                   cursor.execute(statement, (mod_id,))
                   connection.commit()
                   cursor.close()

In update method, id of the moderator and the updated nickname is received and the moderator is updated related to the information.

   .. code-block:: python

       def update_moderator(self, mod_id, newName):
           with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   statement ="""UPDATE MODERATORS
                   SET NICKNAME = (%s)
                   WHERE (ID = (%s))"""
                   cursor.execute(statement, (newName, mod_id))
                   connection.commit()
                   cursor.close()

Below, four get methods can be seen. get_moderator() gets nickname of the moderator and it returns all the imageposts that the corresponding
moderator has been posted. get_moderatorName(self, modid) gets id of the moderator does the same thing as get_moderator().
get_moderators(self) returns all the moderators. get_moderatorObj(self, mod_name) returns the moderator object with the given moderator nickname
'mode_name'.

   .. code-block:: python

       def get_moderator(self, modName):
               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """SELECT ID FROM MODERATORS WHERE (NICKNAME = (%s))"""
                   cursor.execute(query, (modName, ))
                   mod_id = cursor.fetchone()
                   #imgid, imgname, modid
                   connection.commit()
                   cursor.close()
               return mod_id

       def get_moderatorName(self, modid):
               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """SELECT NICKNAME FROM MODERATORS WHERE (ID = (%s))"""
                   cursor.execute(query, (modid, ))
                   modName = cursor.fetchone()
                   #imgid, imgname, modid
                   connection.commit()
                   cursor.close()
               return modName

       def get_moderators(self):
               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """SELECT ID, NICKNAME, PASSWORD FROM MODERATORS
                   ORDER BY ID"""
                   cursor.execute(query)
                   modTable = [(id, Moderator(nickname, password))
                             for id, nickname, password in cursor]
                   connection.commit()
                   cursor.close()
               return modTable

       def get_moderatorObj(self, mod_name):   # def get_user
               with dbapi2.connect(app.config['dsn']) as connection:
                   cursor = connection.cursor()
                   query = """SELECT PASSWORD FROM MODERATORS WHERE (NICKNAME = (%s))"""
                   cursor.execute(query, (mod_name,))
                   mod_pass = cursor.fetchone()
                   connection.commit()
                   if mod_pass is None:
                       mod = None
                   else:
                       mod = Moderator(mod_name, mod_pass[0])  #[0]
                   cursor.close()
                   return mod


There is also profile page of the moderator. It uses get_moderators() method to get all the moderators. In profile page, the current moderator can
see other moderators as well. See user manual for screenshots.

   .. code-block:: python

      @mods.route('/profile', methods=['GET', 'POST'])
      @login_required
      def profile_page():
          moderators = current_app.moderatorlist.get_moderators()
          return render_template('profile.html', moderators=moderators)

'/moderators' route is admin panel. This page is explained in 'Admin' part. moderators_page() method uses get_moderators() to post all the moderators.

   .. code-block:: python

      @mods.route('/moderators')
      @login_required
      def moderators_page():
          moderators = current_app.moderatorlist.get_moderators()
          return render_template('moderators.html', moderators=moderators)


**Image Posts**

Class of the image post is below. It includes name of the image, and foreign key id of the moderator.

   .. code-block:: python

      class ImgPost:
          def __init__(self, imgname, modid):
              self.imgname = imgname
              self.modid = modid
          def change_nickname(self, newimgname):
              self.imgname = newimgname

ImgPostList class is below. add_imgPost(self, imgPost) inserts the given image post object to the database. delete_imgPost(self, imgPost_id)
deletes the image post from the database using its id. update_imgPost(self, imgPost_id, newName) works similarly as update_moderator(self, mod_id, newName).
get_imgPost(self, imgName) returns the id, name and id of the moderator of the given image post. get_imgPostList(self) returns all the image posts
along with the moderators who posted them.

   .. code-block:: python

      class ImgPostList:
          def __init__(self):
                  self.last_key = None

          def add_imgPost(self, imgPost):
                  with dbapi2.connect(app.config['dsn']) as connection:
                      cursor = connection.cursor()
                      query = """INSERT INTO IMGPOSTS (IMGNAME, MODID) VALUES (%s, %s)"""
                      cursor.execute(query, (imgPost.imgname, imgPost.modid))
                      connection.commit()

          def delete_imgPost(self, imgPost_id):
                  with dbapi2.connect(app.config['dsn']) as connection:
                      cursor = connection.cursor()
                      #toBeDeleted = ImgPostList.get_imgPost(imgPost_id)
                      #for row in cursor:
                      #    id, nickname = row
                      statement ="""DELETE FROM IMGPOSTS WHERE (IMGID = (%s))"""
                      cursor.execute(statement, (imgPost_id,))
                      connection.commit()

          def update_imgPost(self, imgPost_id, newName):
              with dbapi2.connect(app.config['dsn']) as connection:
                      cursor = connection.cursor()
                      statement ="""UPDATE IMGPOSTS
                      SET IMGNAME = (%s)
                      WHERE (IMGID = (%s))"""
                      cursor.execute(statement, (newName, imgPost_id))
                      connection.commit()


          def get_imgPost(self, imgName):
                  with dbapi2.connect(app.config['dsn']) as connection:
                      cursor = connection.cursor()
                      query = """SELECT IMGID FROM IMGPOSTS WHERE (IMGNAME = (%s))"""
                      cursor.execute(query, (imgName, ))
                      imgid = cursor.fetchone()
                      #imgid, imgname, modid
                      connection.commit()
                  return imgid

          def get_imgPostList(self):
                  #modid = app.get_moderator(current_user.nickname)
                  with dbapi2.connect(app.config['dsn']) as connection:
                      cursor = connection.cursor()
                      query = """SELECT IMGID, IMGNAME, MODID, NICKNAME FROM IMGPOSTS JOIN
                      MODERATORS ON MODID=ID
                      ORDER BY IMGID"""
                      cursor.execute(query)
                      imgPostTable = [(id, ImgPost(imgname, modid), modname)
                                for id, imgname, modid, modname in cursor]
                  return imgPostTable

Routes for the image posts are given below. Their approach is pretty similar to moderators routes' approach. imgposts_page() provides
image posts feed using get_imgPostList(). imgpost_add_page() adds the image post with given name and using current_user it validates
the information of the moderator who posted it and creates image post object according to that. imgpost_remove_page() deletes the image post
with given name using get_imgPost(imgname) and delete_imgPost(imgid). Finally, imgpost_update_page() updates corresponding image post using
get_imgPost(imgname) and update_imgPost(imgid, newimgname).

   .. code-block:: python

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
