Installation Guide
==================

Following programs and extensions must be downloaded in order to run this project.

**Python**

To download Python 3.5 go to:

   .. _a link: https://www.python.org/downloads/

**Flask**

Flask framework is used in this project. You can instal Flask by typing:

   .. code-block:: python

      pip install flask

Some packages of the Flask and Python are needed to be downloaded as well. These are psycopg2, flask-login and passlib.
You can use the command above to download these.

**PostgreSQL**

To download PostgreSQL go to:

   .. _a link: https://www.postgresql.org/download/

After having downloaded all above, you must setup local database. When the setup of local database is done, make sure
you arrange 'post', 'user' and 'password' according to your choice.

   .. code-block:: python

      if __name__ == '__main__':
       VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
       if VCAP_APP_PORT is not None:
           port, debug = int(VCAP_APP_PORT), False
       else:
           port, debug = 5000, True

       VCAP_SERVICES = os.getenv('VCAP_SERVICES')
       if VCAP_SERVICES is not None:
           app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
       else:
           app.config['dsn'] = """user='vagrant' password='vagrant'
                                  host='localhost' port=5432 dbname='itucsdb'"""
       app.run(host='0.0.0.0', port=port, debug=debug)

**Running the project**

Finally, you can run the project by following command in Python:

   .. code-block:: python

      python server.py