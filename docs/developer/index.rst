Developer Guide
===============

Database Design
---------------
The database contains the following 9 tables:

 - MODERATORS
 - PLACES
 - EVENTS
 - ANNOUNCEMENTS
 - TEXTPOSTS
 - IMGPOSTS
 - HASHTAGS
 - HASHTAGCONTENTS
 - TOPICS
 
 MODID attribute of MODERATORS table is referenced by TEXTPOSTS, IMGPOSTS and TOPICS tables.
 AREA_ID attribute of PLACES table is referenced by EVENTS and ANNOUNCEMENTS tables.
 ID attribute of HASHTAGS table is referenced by the HASHTAGCONTENTS table.
 
 Any further details can be found in the following descriptions of team members.
 
	.. figure:: ERDiagram.png
	      :alt: E/R Diagram of ShakeSpace

Code
----

**explain the technical structure of your code**

**to include a code listing, use the following example**::

   .. code-block:: python

      class Foo:

         def __init__(self, x):
            self.x = x

.. toctree::

   member1
   member2
   member3
   member4
   member5
