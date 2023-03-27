import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ('SECRET_KEY')

DEBUG = False
ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://'+ os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

# Configure Postgres database; the full username for PostgreSQL flexible server is
# username (not @sever-name).
DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ['DBUSER'] + "@" + os.environ['DBHOST'],
    dbpass='PASSWORDORTOKEN',
    dbhost=os.environ['DBHOST'] + ".postgres.database.azure.com",
    dbname=os.environ['DBNAME']
)
