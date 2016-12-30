Parts Implemented by Mumtaz Cem Eris
====================================

**Tables**

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

Route '/login' is for the visitors who have an account already. login_page() would first get the nickname, and using get_moderatorObj(), the moderator
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
namely the admin panel in which the admin can add, remove or update moderators. It is a bit mentioned in 'User Manual' of my part with visual
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

Below, 4 get methods can be seen. get_moderator() gets nickname of the moderator and it returns all the imageposts that the corresponding
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
