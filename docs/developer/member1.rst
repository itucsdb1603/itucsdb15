Parts Implemented by İpek Karakurt
================================
Events
########
Events Table Initialization
***********
The events table is initialized in server.py as follows

.. code-block:: python
	:linenos:
	
	def init_events_db():
	    with dbapi2.connect(app.config['dsn']) as connection:
	        cursor = connection.cursor()
	        query = """DROP TABLE IF EXISTS EVENTS"""
	        cursor.execute(query)
	
	        query = """CREATE TABLE EVENTS (
	        ID SERIAL NOT NULL,
	        CONTENT VARCHAR(300),
	        EVENT_DATE DATE,
	        AREA_ID INTEGER,
	        PRIMARY KEY(ID)
	        )"""
	        cursor.execute(query)
	
	        query = """ALTER TABLE EVENTS
	        ADD FOREIGN KEY(AREA_ID)
	        REFERENCES PLACES(AREA_ID)
	        ON DELETE CASCADE"""
	        cursor.execute(query)
	
	        return redirect(url_for('site.home_page'))
	        
Events entity has four attributes.
 - **ID:** ID is a serial value that is incremented as new events are added. It is the primary key for this entity.
 - **CONTENT:** Content is of type VARCHAR with a limit of 300 characters. It is designed to hold the name of the event.
 - **EVENT_DATE:** This attribute is of type DATE, it holds the date of the event in the YYYYMMDD format.
 - **AREA_ID:** This attribute is a foreign key referencing the AREA_ID attribute from the PLACES table. This is done so that when a new place is added to the places table, it is automatically included as an option for an event's place. 
 
Event Class Definition
***********
The event class is defined in event.py as follows

.. code-block:: python
	:linenos:
	
	class Event:
	    def __init__(self, content, event_date, place):
	        self.content = content
	        self.event_date = event_date
	        self.place = place
	    
	    def update_event(self, new_content, new_place, new_date):
	        self.content = new_content
	        self.event_date = new_date
	        self.place = new_place
	        
Event class has content, event_date and place attributes. When an event needs to be updated, update_event() function takes care of this operation and takes new_content, new_place and new_date as parameters, which represent the newly updated values for the event object. These parameters are then used to set the object's attributes according to the updated event attributes.
 
Event List Class Definition
***********
The event list class is used to keep a list of events that are currently kept in the database. It is defined in eventlist.py as follows:

.. code-block:: python
	:linenos:
	
	class EventList:
	    def __init__(self):
	            self.events = {}
	            self.last_event_id = 0
	
	    def add_event(self, event):
	            self.last_event_id += 1
	            self.events[self.last_event_id] = event
	            event._id = self.last_event_id
	
	    def delete_event(self, event_id):
	            del self.events[event_id]
	
	    def get_event(self, event_id):
	            return self.events[event_id]
	
	    def get_events(self):
	            return self.events
	            
Initially, this list is empty with the last_event_id being 0. As events are added, last_event_id is incremented, newly added event is added to the list and its ID is set. 
delete_event() function takes the event's ID as parameter and deletes the event with this ID from the list of events.
get_event() function also  takes the event's ID as parameter and returns the event with the given ID from the list of events.
Lastly, get_events() function returns the whole list of events.

Event Adding Operation
***********
The event adding operation is defined in the blueprint eventsB.py as follows

.. code-block:: python
	:linenos:
	
	@events.route('/events', methods = ['GET', 'POST'])
	def events_page():
	    if request.method == 'GET':
	        events = current_app.eventlist.get_events()
	        places = current_app.placelist.get_places()
	        return render_template('events.html', events=sorted(events.items()), places=sorted(places.items()))
	    else:
	        content = str(request.form['content'])
	        place = str(request.form['option'])
	        event_date = str(request.form['event_date'])
	        with dbapi2.connect(app.config['dsn']) as connection:
	            cursor = connection.cursor()
	            statement = """SELECT AREA_ID, AREA FROM PLACES WHERE (AREA=(%s))"""
	            cursor.execute(statement, (place,))
	            connection.commit()
	            for row in cursor:
	                area_id, place = row
	            statement ="""INSERT INTO EVENTS (CONTENT, EVENT_DATE, AREA_ID) VALUES (%s, %s, %s)"""
	            cursor.execute(statement, (content, event_date, area_id,))
	            connection.commit()
	
	            event = Event(content, event_date, place)
	
	            current_app.eventlist.add_event(event)
	            return redirect(url_for('events.events_page', event_id=event._id))
		
When the user goes to the events page, they can both see the list of current events and the form that prompts the user to user to enter a new event. If the HTTP request sent by the user is of type GET, "events.html" page is rendered with the additional parameters places and events, which contain the list of places and the list of events in the database respectively. The list of places is passed as a parameter to the render function so that the places can be displayed as options in the dropdown list included in the form to add a new event.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the events page and wants to add a new event. Content, event_date and place variables are initialized with values from the form. The place variable is a text value, however its ID in the PLACES table is needed to add an event to the EVENTS table, as the event entity takes area ID as its foreign key. Therefore, a database query is needed. In this query, the place with the given AREA attribute (which corresponds to city name) is searched for its ID. This ID is kept in area_id variable.
Then, a new event is inserted into the EVENTS table in the database with the content and event_date values from the form and the area_id value from the result of the previous database query.
Then, a new event object is created with content, event_date and place parameters and this object is added to the event list.
The user is redirected to the events page, where they can see the newly added event on the bottom of the list.


Event Deleting Operation
***********
The event deleting operation is defined in the blueprint eventsB.py as follows

.. code-block:: python
	:linenos:
	
	@events.route('/events/delete', methods=['GET', 'POST'])
	def delete_event():
	    if request.method == 'GET':
	        return render_template('delete_event.html')
	    else:
	        content = str(request.form['content'])
	        with dbapi2.connect(app.config['dsn']) as connection:
	            cursor = connection.cursor()
	            statement ="""SELECT ID, CONTENT FROM EVENTS WHERE (CONTENT = (%s))"""
	            cursor.execute(statement, (content,))
	            connection.commit()
	            for row in cursor:
	                id, content = row
	            statement ="""DELETE FROM EVENTS WHERE (ID = (%s))"""
	            cursor.execute(statement, (id,))
	            connection.commit()
	            current_app.eventlist.delete_event(id)
	            return redirect(url_for('events.events_page'))
		
When the user goes to the /events/delete page, they see a form that prompts them to enter an event's name to delete it. If the HTTP request sent by the user is of type GET, "delete_event.html" page is rendered which contains the said form.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the page and wants to delete an existing event. Content is initialized with the value from the form. The event's ID in the EVENTS table is needed. Therefore, a database query is done. In this query, the event with the given CONTENT attribute is searched for its ID.
This ID is kept in id variable.
Then, the event is deleted from the EVENTS table in the database with the id value obtained from the result of the previous database query.
Then, the event object with the said id is deleted from the event list.
The user is redirected to the events page, where they can see that the event they deleted disappeared from the list of events displayed on that page.

Event Updating Operation
***********
The event updating operation is defined in the blueprint eventsB.py as follows

.. code-block:: python
	:linenos:
	
	@events.route('/events/update', methods = ['GET', 'POST'])
	def update_event():
	    if request.method == 'GET':
	        events = current_app.eventlist.get_events()
	        places = current_app.placelist.get_places()
	        return render_template('update_event.html', events=sorted(events.items()), places=sorted(places.items()))
	    else:
	        content = str(request.form['content'])
	        new_content = str(request.form['new_content'])
	        new_place = str(request.form['option'])
	        new_date = str(request.form['new_date'])
	        with dbapi2.connect(app.config['dsn']) as connection:
	            cursor = connection.cursor()
	            statement = """SELECT AREA_ID, AREA FROM PLACES WHERE (AREA=(%s))"""
	            cursor.execute(statement, (new_place,))
	            connection.commit()
	            for row in cursor:
	                area_id, place = row
	
	            cursor = connection.cursor()
	            statement = """UPDATE EVENTS
	            SET CONTENT = (%s),
	            EVENT_DATE = (%s),
	            AREA_ID = (%s)
	            WHERE (CONTENT=(%s))"""
	            cursor.execute(statement, (new_content, new_date, area_id, content))
	            connection.commit()
	
	            cursor = connection.cursor()
	            statement = """SELECT ID, CONTENT FROM EVENTS WHERE (CONTENT = (%s))"""
	            cursor.execute(statement, (new_content,))
	            connection.commit()
	            for row in cursor:
	                id, content = row
	
	            updated_event = current_app.eventlist.get_event(id)
	            updated_event.update_event(new_content, new_place, new_date)
	            return redirect(url_for('events.events_page'))

When the user goes to the /events/update page, they see a form that prompts them to enter an event's name to update it. The form also contains the updated name, the updated date and the updated place input fields.
If the HTTP request sent by the user is of type GET, "update_event.html" page is rendered which contains the said form. This function takes the parameters events and places lists, the former will be used to display the current list of events on the top of the page and the latter to display the place names as options in a dropdown list in the update form.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the page and wants to update an existing event. new_content, new_date and new_place variables which are used to keep the updated attributes of the event, and the content variable which is used to keep the name of the event to be updated are initialized with the values from the form. 
The new_place variable is a text value, however its ID in the PLACES table is needed to update an event on the EVENTS table, as the event entity takes area ID as its foreign key. Therefore, a database query is needed. In this query, the place with the given AREA attribute (which corresponds to city name) is searched for its ID. This ID is kept in area_id variable.
Then, the event is updated in the EVENTS table in the database where the content of the previously added event matches the content variable initialized from the form value. That event's content, date and area attributes are set to their new values.
The ID of the currently updated event is needed to pass as an argument to the get_event() function, in order to update the event object. A database query is done in order to get to ID from the EVENTS table with a set content attribute.
Then, the event object with the said id selected as updated_event from the event list.
update_event() method is invoked on this object with new_content, new_place and new_date arguments so that the object is updated with these values.
The user is redirected to the events page, where they can see that the event they updated is changed as wanted in the list of events displayed on that page.

Places
########
Places Table Initialization
***********
The places table is initialized in the blueprint placesB.py as follows

.. code-block:: python
	:linenos:
	
	@places.route('/initplaces')
	def init_places_db():
	    with dbapi2.connect(app.config['dsn']) as connection:
	        cursor = connection.cursor()
	
	        query = """DROP TABLE IF EXISTS PLACES CASCADE"""
	        cursor.execute(query)
	
	        query = """CREATE TABLE PLACES (
	        AREA_ID SERIAL,
	        AREA VARCHAR(300),
	        PRIMARY KEY(AREA_ID)
	        )"""
	        cursor.execute(query)
	        connection.commit()
	        return redirect(url_for('site.home_page'))
	        
Places entity has two attributes.
 - **AREA_ID:** Area ID is a serial value that is incremented as new places are added. It is the primary key for this entity.
 Area ID is referenced as a foreign key in the EVENTS table as well as the ANNOUNCEMENTS table.
 - **AREA:** Area is of type VARCHAR with a limit of 300 characters. It is designed to hold the name of the place.
 
Place Class Definition
***********
The place class is defined in place.py as follows

.. code-block:: python
	:linenos:
	
	class Place:
	    def __init__(self, area):
	        self.area = area
	    
	    def update_place(self, new_area):
	        self.area = new_area
	        
Place class has the area attribute. When a place needs to be updated, update_place() function takes care of this operation and takes new_area, which represents the newly updated area name value for the place object. This parameter is then used to set the place object's attributes according to the updated place's attributes.
 
Place List Class Definition
***********
The place list class is used to keep a list of places that are currently kept in the database. This list is beneficial to keep in order to print out the place options for an event in a dropdown list. It is defined in placelist.py as follows:

.. code-block:: python
	:linenos:
	
	class PlaceList:
	    def __init__(self):
	            self.places = {}
	            self.last_place_id = 0
	
	    def add_place(self, place):
	            self.last_place_id += 1
	            self.places[self.last_place_id] = place
	            place._id = self.last_place_id
	
	    def delete_place(self, place_id):
	            del self.places[place_id]
	
	    def get_place(self, place_id):
	            return self.places[place_id]
	
	    def get_places(self):
	            return self.places

	            
Initially, this list is empty with the last_event_id being 0. As places are added, last_place_id is incremented, newly added place is added to the list and its ID is set. 
delete_place() function takes the place's ID as parameter and deletes the place with this ID from the list of events.
get_place() function also  takes the place's ID as parameter and returns the place with the given ID from the list of places.
Lastly, get_places() function returns the whole list of places.

Place Adding Operation
***********
The place adding operation is defined in the blueprint placesB.py as follows

.. code-block:: python
	:linenos:
	
	@places.route('/places', methods = ['GET', 'POST'])
	def places_page():
	    if request.method == 'GET':
	        places = current_app.placelist.get_places()
	        return render_template('places.html', places=sorted(places.items()))
	    else:
	        area = str(request.form['area'])
	        with dbapi2.connect(app.config['dsn']) as connection:
	            cursor = connection.cursor()
	
	            statement ="""INSERT INTO PLACES (AREA) VALUES (%s)"""
	            cursor.execute(statement, [area])
	            connection.commit()
	
	            place = Place(area)
	
	            current_app.placelist.add_place(place)
	            return redirect(url_for('places.places_page', place_id=place._id))
		
When the user goes to the places page, they can both see the list of current places and the form that prompts the user to user to enter a new place. If the HTTP request sent by the user is of type GET, "places.html" page is rendered with the additional parameter places, which contains the list of places in the database. This is passed as a parameter to the render function so that the list of places can be displayed on the page.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the places page and wants to add a new place. Area variable is initialized with its value from the form. 
Then, a new place is inserted into the PLACES table in the database with the this area value.
Then, a new place object is created with the area value and this object is added to the place list.
The user is redirected to the places page, where they can see the newly added place on the bottom of the list.

Place Deleting Operation
***********
The place deleting operation is defined in the blueprint placesB.py as follows

.. code-block:: python
	:linenos:
	
	@places.route('/places/delete', methods=['GET', 'POST'])
	def delete_place():
	    if request.method == 'GET':
	        return render_template('delete_place.html')
	    else:
	        area = str(request.form['area'])
	        with dbapi2.connect(app.config['dsn']) as connection:
	            cursor = connection.cursor()
	            statement ="""SELECT AREA_ID, AREA FROM PLACES WHERE (AREA = (%s))"""
	            cursor.execute(statement, (area,))
	            connection.commit()
	            for row in cursor:
	                id, area = row
	            statement ="""DELETE FROM PLACES WHERE (AREA_ID = (%s))"""
	            cursor.execute(statement, (id,))
	            connection.commit()
	            current_app.placelist.delete_place(id)
	            return redirect(url_for('places.places_page'), place_id=place._id)
		
When the user goes to the /places/delete page, they see a form that prompts them to enter a place to delete it. If the HTTP request sent by the user is of type GET, "delete_place.html" page is rendered which contains the said form.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the page and wants to delete an existing place. area is initialized with the value from the form. The place's ID in the PLACES table is needed. Therefore, a database query is conducted. In this query, the event with the given AREA attribute is searched for its AREA_ID.
This ID is kept in id variable.
Then, the place is deleted from the PLACES table in the database with the id value obtained from the result of the previous database query.
Then, the place object with the said id is deleted from the place list.
The user is redirected to the places page, where they can see that the place they deleted disappeared from the list of places displayed on that page.

Place Updating Operation
***********
The place updating operation is defined in the blueprint placesB.py as follows

.. code-block:: python
	:linenos:
	
	@places.route('/places/update', methods=['GET', 'POST'])
	def update_place():
	    if request.method == 'GET':
	        return render_template('update_place.html')
	    else:
	        area= str(request.form['area'])
	        new_area = str(request.form['new_area'])
	        with dbapi2.connect(app.config['dsn']) as connection:
	            cursor = connection.cursor()
	            statement ="""UPDATE PLACES
	            SET AREA = (%s)
	            WHERE AREA = (%s)"""
	            cursor.execute(statement, (new_area, area,))
	            connection.commit()
	
	            cursor = connection.cursor()
	            statement = """SELECT AREA_ID, AREA FROM PLACES WHERE (AREA = (%s))"""
	            cursor.execute(statement, (new_area,))
	            connection.commit()
	            for row in cursor:
	                area_id, area = row
	
	            updated_place = current_app.placelist.get_place(area_id)
	            updated_place.update_place(new_area)
	            return redirect(url_for('places.places_page'), place_id=place._id)
            
When the user goes to the /places/update page, they see a form that prompts them to enter an place's name to update it. The form also contains the updated place input fields.
If the HTTP request sent by the user is of type GET, "update_place.html" page is rendered which contains the said form. 
If the HTTP request sent by the user is of type POST, then the user filled in the form on the page and wants to update an existing place. new_area variable which is used to keep the updated attributes of the area, and the area variable which is used to keep the old name of the area to be updated are initialized with the values from the form. 
Then, the event is updated in the PLACES table in the database where the content of the previously added place matches the area variable initialized from the form value. That place's AREA attribute is set to its new value, new_area.
The ID of the currently updated place is needed to pass as an argument to the get_place() function, in order to update the place object. A database query is done in order to get the AREA_ID from the PLACES table with a set area attribute.
Then, the event object with the said area ID is selected as updated_place from the event list.
update_place() method is invoked on this object with new_area argument so that the object is updated with these values.
The user is redirected to the places page, where they can see that the place they updated is changed as wanted in the list of places displayed on that page.

Text Posts
########
Text Posts Table Initialization
***********
The text posts table is initialized in the server.py as follows

.. code-block:: python
	:linenos:
	
	@app.route('/inittextposts')
	def init_posts():
	    with dbapi2.connect(app.config['dsn']) as connection:
	        cursor = connection.cursor()
	
	        query = """DROP TABLE IF EXISTS TEXTPOSTS CASCADE"""
	        cursor.execute(query)
	
	        query = """CREATE TABLE TEXTPOSTS(
	        POSTID SERIAL,
	        CONTENT VARCHAR(300),
	        WRITER INTEGER,
	        POSTTOPIC VARCHAR(40),
	        PRIMARY KEY(POSTID),
	        FOREIGN KEY (WRITER) REFERENCES MODERATORS (ID)
	            ON DELETE CASCADE
	            ON UPDATE CASCADE
	        )"""
	        cursor.execute(query)
	
	        connection.commit()
	        return redirect(url_for('site.home_page'))
	        
Text post entity has four attributes.
 - **POSTID:** Post ID is a serial value that is incremented as new text posts are added. It is the primary key for this entity.
 - **CONTENT:** Content is of type VARCHAR with a limit of 300 characters. It is designed to hold the text content of the entry.
 - **WRITER:** Writer is of type INTEGER. It is designed to hold the ID of the writer of the entry. Writer attribute reference the MODERATORS table as its foreign key.
 - **POSTTOPIC:** Post topic is of type VARCHAR with a limit of 40 characters. It is designed to hold the topic of the entry. This feature is not fully implemented therefore it does not reference the TOPICS table, this attribute is NULL for every tuple in the TEXTPOSTS table.
 
Text Post Class Definition
***********
The text post class is defined in textpost.py as follows

.. code-block:: python
	:linenos:
	
	class TextPost:
	    def __init__(self, content, writer):
	        self.content = content
	        self.writer = writer
	    def change_textpost(self, new_content):
	        self.content = new_content
	        
Text post class has the content and writer attributes. 
When a text post needs to be updated, change_textpost() function takes care of this operation and takes new_content, which represents the newly updated content value for the text post object. This parameter is then used to set the text post object's content attribute according to the updated text post's attribute.
Writer does not change with update operation.
 
Text Post List Class Definition
***********
The text post list class is used to keep a list of text posts that are currently kept in the database. This list is beneficial to keep in order to print out the text post list for the user to see. It is defined in textpostlist.py as follows:

.. code-block:: python
	:linenos:
	
	class TextPostList:
	    def __init__(self):
	            self.last_key = None
	
	    def add_TextPost(self, textPost):
	            with dbapi2.connect(app.config['dsn']) as connection:
	                cursor = connection.cursor()
	                query = """INSERT INTO TEXTPOSTS (CONTENT, WRITER) VALUES (%s, %s)"""
	                cursor.execute(query, (textPost.content, textPost.writer))
	                connection.commit()
	
	    def delete_TextPost(self, TextPost_id):
	            with dbapi2.connect(app.config['dsn']) as connection:
	                cursor = connection.cursor()
	                statement ="""DELETE FROM TEXTPOSTS WHERE (POSTID = (%s))"""
	                cursor.execute(statement, (TextPost_id,))
	                connection.commit()
	
	    def update_TextPost(self, TextPost_id, new_content):
	        with dbapi2.connect(app.config['dsn']) as connection:
	                cursor = connection.cursor()
	                statement ="""UPDATE TEXTPOSTS
	                SET CONTENT = (%s)
	                WHERE (POSTID = (%s))"""
	                cursor.execute(statement, (new_content, TextPost_id,))
	                connection.commit()
	
	    def get_TextPost(self, content):
	            with dbapi2.connect(app.config['dsn']) as connection:
	                cursor = connection.cursor()
	                query = """SELECT POSTID FROM TEXTPOSTS WHERE (CONTENT = (%s))"""
	                cursor.execute(query, (content, ))
	                TextPost_id = cursor.fetchone()  
	                connection.commit()
	            return TextPost_id
	
	    def get_TextPostList(self):
	            with dbapi2.connect(app.config['dsn']) as connection:
	               cursor = connection.cursor()
	               query = """SELECT POSTID, CONTENT, WRITER, NICKNAME FROM TEXTPOSTS JOIN
	                MODERATORS ON WRITER=ID
	                ORDER BY POSTID"""
	               cursor.execute(query)
	               TextPostTable = [(id, TextPost(content, writer), modname)
	                          for id, content, writer, modname in cursor]
	            return TextPostTable
	        
	    def get_TextPostListofMod(self, writer):
	            with dbapi2.connect(app.config['dsn']) as connection:
	               cursor = connection.cursor()
	               query = """SELECT POSTID, CONTENT, WRITER, NICKNAME FROM TEXTPOSTS JOIN
	                MODERATORS ON WRITER=ID
	                WHERE WRITER = (%s)
	                ORDER BY POSTID"""
	               cursor.execute(query, (writer,))
	               TextPostTableofMod = [(id, TextPost(content, writer), modname)
	                          for id, content, writer, modname in cursor]
	            return TextPostTableofMod
	            
Initially, this list is empty with the last_key being None. 
As text posts are added, text post objects are created in the textpostsB.py blueprint, where they are also passed to the add_TextPost() function as a parameter. Here they are inserted to the database.
delete_TextPost() function takes the post's ID as parameter and deletes the place with this ID from the database.
update_TextPost() function takes the new content of the post in addition to the post's ID as parameters and sets the content of the text post to the new content in the database.
get_TextPost() function also  takes the post's content as parameter and returns the post with the given content from the TEXTPOSTS table in the database.
get_TextPostList() function returns the posts from the TEXTPOSTS table in the database. The writer's ID is referenced as a foreign key from the MODERATORS table and kept in the TEXTPOSTS table therefore in order to get and display the writer's name, a JOIN operation is done with the MDOERATORS table.
Lastly, get_TextPostListofMod() function works in a similar fashion to get_TextPostList() but it returns the text posts from the currently logged in writer only. 

Text Post Adding Operation
***********
In addition to the add operation described in Text Post List Class Definition section, adding operation is done in the blueprint textpostsB.py as follows

.. code-block:: python
	:linenos:
	
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
		
When the user goes to the /textposts/add_text_posts page, they see the form that prompts the user to user to enter a new post.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the text posts page and wants to add a new post. Content variable is initialized with its value from the form. Writer is initialized by making use of the current_user proxy, to get the ID of this user get_moderator() function is used. 
Then, a new TextPost object is created with the content and writer variables and this object is sent as a parameter to the add_TextPost() function described in the previous section. 
The user is redirected to the text posts page, where they can see the newly added post on the bottom of the list.

Text Post Deleting Operation
***********
In addition to the delete operation described in Text Post List Class Definition section, the text post deleting operation is defined in the blueprint textpostsB.py as follows

.. code-block:: python
	:linenos:
	
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

		
When the user goes to the /textposts/textpost_remove page, they see a form that prompts them to enter a post's content to delete it. If the HTTP request sent by the user is of type GET, "textpost_remove.html" page is rendered which contains the said form.
If the HTTP request sent by the user is of type POST, then the user filled in the form on the page and wants to delete an existing post. Content variable is initialized with the value from the form. 
The post's ID in the TEXTPOSTS table is needed in order to be passed to the delete_TextPost() function. In order to get the post ID, the content is passed to the get_TextPost() function which returns the ID of the post as described above. This ID is kept in postid variable.
Then, the post with the given postid is deleted from the TEXTPOSTS table in the database when it is passed to the delete_TextPost() function.
The user is redirected to the text posts page, where they can see that the post they deleted disappeared from the list of posts displayed on that page.

Text Post Updating Operation
***********
In addition to the update operation described in Text Post List Class Definition section, the text post updating operation is defined in the blueprint textpostsB.py as follows

.. code-block:: python
	:linenos:
	
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
            
When the user goes to the /textposts/textpost_update page, they see a form that prompts them to enter a text post's content to update it. The form also contains the updated text post input field.
If the HTTP request sent by the user is of type GET, "textpost_update.html" page is rendered which contains the said form. 
If the HTTP request sent by the user is of type POST, then the user filled in the form on the page and wants to update an existing text post. new_content variable which is used to keep the updated value of the post content, and the content variable which is used to keep the old content of the post to be updated are initialized with the values from the form. 
The post's ID in the TEXTPOSTS table is needed in order to be passed to the update_TextPost() function. In order to get the post ID, the content is passed to the get_TextPost() function which returns the ID of the post as described above. This ID is kept in postid variable.
Then, the post with the given postid is updated in the TEXTPOSTS table in the database when it is passed to the update_TextPost() function along with the parameters postid and new_content as described in the previous sections.
The user is redirected to the text posts page, where they can see that the post they updated is changed as wanted in the list of posts displayed on that page.

Displaying Text Posts
***********
In order to display the text posts written by the current user on the text posts page, the following logic is used in the Blueprint textpostsB.py

.. code-block:: python

	@TextPosts.route('/textposts')
	@login_required
	def textposts_page():
	    writer = app.moderatorlist.get_moderator(current_user.nickname)
	    textposts = app.textpostlist.get_TextPostListofMod(writer)
	    return render_template('textposts.html', textposts=textposts)

The writer, which is the currently logged in user is initialized by making use of the current_user proxy, to get the ID of this user get_moderator() function is used.
Then, textposts variable is populated with the return value of get_TextPostListofMod() function with the writer variable as a parameter. This variable now contains the list of posts written by the currently logged in user.
Then, textposts.html file is rendered with the additional textposts variable, which allows for displaying the text posts of the currently logged in user on the page.
 