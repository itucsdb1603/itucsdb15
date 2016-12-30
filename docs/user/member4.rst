Parts Implemented by Batuhan İşlek
==================================

Annoucements
############
Announcement Table
******************

Announcements are initiliazed in the server.py :

.. code-block:: python
   :linenos:
   
   @app.route('/init_announcements')
   def init_announcements_db():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS ANNOUNCEMENTS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE ANNOUNCEMENTS (
        ID SERIAL NOT NULL,
        CONTENT VARCHAR(300),
        AREA_ID SERIAL,
        PRIMARY KEY(ID),
        FOREIGN KEY(AREA_ID) REFERENCES PLACES(AREA_ID)
            ON DELETE CASCADE
            ON UPDATE CASCADE
        )"""
        cursor.execute(query)

        connection.commit()
        return redirect(url_for('site.home_page'))
  
Announcement Operations
***********************
All announcement operations are held in the server.py :

.. code-block:: python
   :linenos:
   
   @app.route('/announcements',  methods=['GET', 'POST'])
   def announcements_page():
    if 'add_announcement' in request.form:
        content = str(request.form['CONTENT'])
        area_id = str(request.form['AREA_ID'])
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO ANNOUNCEMENTS (CONTENT, AREA_ID) VALUES (%s, %s)""", [content, area_id])
            connection.commit()
            
    elif 'init_announcements' in request.form:
        init_announcements_db()
        
    elif 'delete_announcement' in request.form:
        delete_id = request.form['delete_id']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute("""DELETE FROM ANNOUNCEMENTS WHERE ID=%s""", delete_id)
            connection.commit()
            
    elif 'edit_announcement' in request.form:
        edit_id = request.form['edit_id']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM ANNOUNCEMENTS WHERE ID=%s""", edit_id)
            selectedAnnouncement = cursor.fetchall()
            connection.commit()
            return render_template('update_announcement.html', announcements = selectedAnnouncement)
            
    elif 'selected_announcement_update' in request.form:
        announcement_id = request.form['id']
        announcement_content = request.form['content']
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            cursor.execute("""UPDATE ANNOUNCEMENTS SET CONTENT=%s WHERE id=%s""", (announcement_content, announcement_id))
            connection.commit()
            
    allAnnouncements = get_announcements()
    allPlaces = current_app.placelist.get_places()
    return render_template('announcements.html', announcements = allAnnouncements, places = allPlaces)

   def get_announcements():
       with dbapi2.connect(app.config['dsn']) as connection:
           import placesB
           cursor = connection.cursor()
   
           cursor.execute("SELECT ID, CONTENT, AREA FROM ANNOUNCEMENTS JOIN PLACES ON (ANNOUNCEMENTS.AREA_ID = PLACES.AREA_ID)")
           announcements = cursor.fetchall()
   
           connection.commit()
   
           return announcements

Topics Class Definition
***********************

.. code-block:: python
   :linenos:
   
    class Topic:
    def __init__(self, content, writer):
        self.content = content
        self.writer = writer
        
Topics List Class Definition
****************************

.. code-block:: python
   :linenos:

    class TopicList:
    def __init__(self):
            self.last_key = None

    def add_topic(self, topic):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO TOPICS (CONTENT, WRITER) VALUES (%s, %s)"""
                cursor.execute(query, (topic.content, topic.writer))
                connection.commit()

    def delete_topic(self, topic_id):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement ="""DELETE FROM TOPICS WHERE (TOP_ID = (%s))"""
                cursor.execute(statement, (topic_id,))
                connection.commit()

    def get_topic(self, content):
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT TOP_ID FROM TOPICS WHERE (CONTENT = (%s))"""
                cursor.execute(query, (content, ))
                topic_id = cursor.fetchone()  
                connection.commit()
            return topic_id

    def get_TopicList(self):
            with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               query = """SELECT TOP_ID, CONTENT, WRITER, NICKNAME FROM TOPICS JOIN
                MODERATORS ON WRITER=ID
                ORDER BY TOP_ID"""
               cursor.execute(query)
               topicTable = [(id, Topic(content, writer), modname)
                          for id, content, writer, modname in cursor]
            return topicTable
        
    def get_TopicListofMod(self, writer):
            with dbapi2.connect(app.config['dsn']) as connection:
               cursor = connection.cursor()
               query = """SELECT TOP_ID, CONTENT, WRITER, NICKNAME FROM TOPICS JOIN
                MODERATORS ON WRITER=ID
                WHERE WRITER = (%s)
                ORDER BY TOP_ID"""
               cursor.execute(query, (writer,))
               topicTableofMod = [(id, Topic(content, writer), modname)
                          for id, content, writer, modname in cursor]
            return topicTableofMod

Topics Adding Operation
***********************

.. code-block:: python
   :linenos:
   
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

Topics Adding Operation
***********************

.. code-block:: python
   :linenos:
   
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
        

Topics Display Operation
************************
 
.. code-block:: python
   :linenos:
 
   @Topics.route('/topics')
   @login_required
   def topics_page():
       writer = app.moderatorlist.get_moderator(current_user.nickname)
       topics = app.topiclist.get_TopicListofMod(writer)
       return render_template('topics.html', topics=topics)
      
