import os
import secrets

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY'] if 'SECRET_KEY' in os.environ else secrets.token_hex()

DEBUG = False
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

if not 'AZURE_POSTGRESQL_CONNECTIONSTRING' in os.environ:
    # Configure Postgres database; the full username for PostgreSQL flexible server is
    # username (not @sever-name).
    DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser=os.environ['DBUSER'] + "@" + os.environ['DBHOST'],
        dbpass='PASSWORDORTOKEN',
        dbhost=os.environ['DBHOST'] + ".postgres.database.azure.com",
        dbname=os.environ['DBNAME']
    )
else:
    # Configure Postgres database based on connection string of the libpq Keyword/Value form
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
    conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

    # Configure Postgres database; the full username for PostgreSQL flexible server is
    # username (without @server-name).
    DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser=conn_str_params['user'],
        dbpass='PASSWORDORTOKEN',
        dbhost=conn_str_params['host'],
        dbname=conn_str_params['dbname']
    )
