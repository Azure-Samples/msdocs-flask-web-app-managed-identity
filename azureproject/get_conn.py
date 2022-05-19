import os
from flask import current_app
from azure.identity import DefaultAzureCredential

def get_conn():
    if 'WEBSITE_HOSTNAME' in os.environ:   
        # Azure hosted, refresh token that becomes password.
        azure_credential = DefaultAzureCredential()
        # Get token for Azure Database for PostgreSQL
        print("Get password token.")
        token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net")
        conn = str(current_app.config.get('DATABASE_URI')).replace('PASSWORDORTOKEN', token.token)
        return conn
    else:
        # Locally, read password from environment variable.
        print("Read password env variable.")
        conn = str(current_app.config.get('DATABASE_URI')).replace('PASSWORDORTOKEN', os.environ['DBPASS'])
        return conn
