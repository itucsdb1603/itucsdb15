Parts Implemented by Emre Can Agatay
================================

**Tables**

There are two tables that are implemented by me. Tables can be seen from the '/init_hashtags/' route which initializes 'HASHTAGS'
and 'HASHTAGCONTENTS'. HASHTAGCONTENTS's HASHTAGID references HASHTAGS's ID.

	.. code-block:: python

      @hashtags.route('/init_hashtags')
	  def init_hashtag_db():
		with dbapi2.connect(app.config['dsn']) as connection:
			cursor = connection.cursor()

			query = """DROP TABLE IF EXISTS HASHTAGCONTENTS"""
			cursor.execute(query)
			query = """DROP TABLE IF EXISTS HASHTAGS CASCADE"""
			cursor.execute(query)

			query = """CREATE TABLE HASHTAGS (
			ID SERIAL NOT NULL,
			NAME VARCHAR(50),
			PRIMARY KEY(ID)
			)"""
			cursor.execute(query)

			query = """CREATE TABLE HASHTAGCONTENTS (
			ID SERIAL,
			HASHTAGID INTEGER,
			CONTENT VARCHAR(300),
			PRIMARY KEY(HASHTAGID, ID),
			FOREIGN KEY(HASHTAGID)
			REFERENCES HASHTAGS(ID)
			ON DELETE CASCADE
			ON UPDATE CASCADE
			)"""
			cursor.execute(query)

			connection.commit()
			return redirect(url_for('site.home_page'))

**Hashtags**

Firstly, Hashtag class will be examined. It has only 'name' variable and 'update_name' method to change the name of the hashtag.

   .. code-block:: python

      class Hashtag:
		def __init__(self, name):
			self.name = name

		def update_name(self, updatedHashtag):
			self.name = updatedHashtag

Hashtags class is below. This class have the methods of adding, deleting, updating and getting one or all hashtags. First, let's see the 
add_hashtag(self, hashtag) method. It inserts the given hashtag object to the database.  

   .. code-block:: python

		def add_hashtag(self, hashtag):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement ="""INSERT INTO HASHTAGS (NAME) VALUES (%s)"""
				cursor.execute(statement, (hashtag.name,))
				connection.commit()

delete_hashtag(self, hashtag_id) gets id of the hashtag as an argument and it deletes the hashtag from the database using its id, after
it deletes the contents that belongs to that hashtag.
				
	.. code-block:: python
	
		def delete_hashtag(self, hashtag_id):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement ="""DELETE FROM HASHTAGCONTENTS WHERE (HASHTAGID = (%s))"""
				cursor.execute(statement, (hashtag_id,))
				connection.commit()
				statement ="""DELETE FROM HASHTAGS WHERE (ID = (%s))"""
				cursor.execute(statement, (hashtag_id,))
				connection.commit()
				cursor.close()

In update method, id of the hashtag and the new hashtag name is received and the hashtag is updated according to that information.
				
	.. code-block:: python

		def update_hashtag(self, hashtag_id, newHashtag):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement ="""UPDATE HASHTAGS SET NAME = (%s) WHERE (ID = (%s))"""
				cursor.execute(statement, (newHashtag, hashtag_id))
				connection.commit()
				cursor.close()

Below, 4 get methods can be seen. get_hashtag(self, name) returns the id of the hashtag with the given name. get_hashtagName(self, hashtag_id) 
returns the name of the hashtag with the given id. get_hashtags(self) returns all the hashtag's id and their name ordered by id. 
get_hashtagObj(self, hashtag_name) returns the hashtag object itself with the given name.
				
	.. code-block:: python

		def get_hashtag(self, name):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement = """SELECT ID FROM HASHTAGS WHERE (NAME = (%s))"""
				cursor.execute(statement, (name,))
				hashtag_id = cursor.fetchone()
				connection.commit()
				cursor.close()
				return hashtag_id

		def get_hashtagName(self, hashtag_id):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement = """SELECT NAME FROM HASHTAGS WHERE (ID = (%s))"""
				cursor.execute(statement, (hashtag_id, ))
				hashtagName = cursor.fetchone()
				connection.commit()
				cursor.close()
				return hashtagName

		def get_hashtags(self):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement = """SELECT ID, NAME FROM HASHTAGS ORDER BY ID"""
				cursor.execute(statement)
				hashtagTable = [(id, Hashtag(name))
						  for id, name in cursor]
				connection.commit()
				cursor.close()
				return hashtagTable

		def get_hashtagObj(self, hashtag_name):
            hashtag = Hashtag(hashtag_name)
            return hashtag
			
Routes for the hashtags are given below. hashtags_page() provides hashtags feed using get_hashtags(). hashtag_page(hashtag_id) provides hashtagContents feed 
using get_contents(). hashtag_add_page() adds the hashtag with given name and creates hashtag object. hashtag_remove_page() deletes the hashtag 
with given name using get_hashtag(name) and delete_hashtag(hashtagid). Finally, hashtag_update_page() updates corresponding hashtag using
get_hashtag(imgname) and update_hashtag(hashtag_id, newhashtag).

	.. code-block:: python

		@hashtags.route('/hashtags')
		def hashtags_page():
			hashtags = current_app.hashtags.get_hashtags()
			return render_template('hashtags.html', hashtags = hashtags)

		@hashtags.route('/hashtag/<int:hashtag_id>')
		def hashtag_page(hashtag_id):
			hashtag_name = current_app.hashtags.get_hashtagName(hashtag_id)
			hashtag = current_app.hashtags.get_hashtagObj(hashtag_name)
			hashtagContents = current_app.hashtagContents.get_contents(hashtag_id)
			return render_template('hashtag.html', hashtag=hashtag, hashtagContents = hashtagContents, hashtagid = hashtag_id)

		@hashtags.route('/hashtags/add', methods=['GET', 'POST'])
		def hashtag_add_page():
			if request.method == 'GET':
				return render_template('hashtag_add.html')
			else:
				name = str(request.form['name'])
				hashtag = Hashtag(name)
				current_app.hashtags.add_hashtag(hashtag)
				hashtag_id = current_app.hashtags.get_hashtag(hashtag.name)
				return redirect(url_for('hashtags.hashtags_page'))

		@hashtags.route('/hashtags/update', methods=['GET', 'POST'])
		def hashtag_update_page():
			if request.method == 'GET':
				return render_template('hashtag_update.html')
			else:
				name = str(request.form['name'])
				newhashtag = str(request.form['newhashtag'])
				hashtag_id = current_app.hashtags.get_hashtag(name)
				current_app.hashtags.update_hashtag(hashtag_id, newhashtag)
				return redirect(url_for('hashtags.hashtags_page'))

		@hashtags.route('/hashtags/remove', methods=['GET', 'POST'])
		def hashtag_delete_page():
			if request.method == 'GET':
				return render_template('hashtag_delete.html')
			else:
				name = str(request.form['name'])
				hashtag_id = current_app.hashtags.get_hashtag(name)
				current_app.hashtags.delete_hashtag(hashtag_id)
				return redirect(url_for('hashtags.hashtags_page'))


**HashtagContents**			

After we examine the hashtag class, we can proceed with the HashtagContent class which represents the comments about the hashtags.
This class has 'content' variable and forign key id of the hashtag.


	.. code-block:: python
		class HashtagContent:
			def __init__(self, content, hashtagid):
				self.content = content
				self.hashtagid = hashtagid
			def update_content(self, updatedContent):
				self.content = updatedContent
				
HashtagContents class is below. This class has the similar methods with the Hashtags class such as add, delete, update and get content. add_content(self, hashtagcontent)
inserts the given content object to the database. delete_content(self, hashtagid, contentid) deletes the content from the database using its id and hashtag id. 
update_content(self, hashtagid, content_id, newcontent) changes the content with the given id and hashtagid.
get_contents(self, hashtagid) returns all contents of a hashtag with their content id and hashtag id.

	.. code-block:: python
				
		def add_content(self, hashtagcontent):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement ="""INSERT INTO HASHTAGCONTENTS (HASHTAGID, CONTENT) VALUES (%s, %s)"""
				cursor.execute(statement, (hashtagcontent.hashtagid, hashtagcontent.content))
				connection.commit()

		def delete_content(self, hashtagid, contentid):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement ="""DELETE FROM HASHTAGCONTENTS WHERE (ID = (%s) AND HASHTAGID = (%s))"""
				cursor.execute(statement, (contentid, hashtagid))
				connection.commit()

		def update_content(self, hashtagid, content_id, newcontent):
			with dbapi2.connect(app.config['dsn']) as connection:
				cursor = connection.cursor()
				statement ="""UPDATE HASHTAGCONTENTS SET CONTENT = (%s) WHERE (ID = (%s) AND HASHTAGID = (%s))"""
				cursor.execute(statement, (newcontent, content_id, hashtagid))
				connection.commit()

		def get_contents(self, hashtagid):
				with dbapi2.connect(app.config['dsn']) as connection:
					cursor = connection.cursor()
					statement = """SELECT ID, HASHTAGID, CONTENT FROM HASHTAGCONTENTS WHERE HASHTAGID = (%s) ORDER BY ID"""
					cursor.execute(statement, (hashtagid,))
					contents = [(id, HashtagContent(hashtagid, content))
							  for id, hashtagid, content in cursor]
				return contents
				
Routes for the hashtag contents are given below. Their approach is pretty similar to hashtags routes' approach. hashtagContent_add_page(hashtag_id) 
creates the content with given name and hashtag id and adds it using add_content(hashtag_content). hashtagContent_delete_page(hashtag_id) deletes 
the hashtag content with given hashtag id using delete_content(hashtag_id, contentid). Finally, hashtagContent_update_page(hashtag_id) updates corresponding 
hashtag content using update_content(hashtag_id, contentid, newContent).

   .. code-block:: python
   
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