import os
from flask import current_app
from azure.identity import DefaultAzureCredential

def get_conn():
    # Azure hosted, refresh token that becomes password.
    azure_credential = DefaultAzureCredential()
    # Get token for Azure Database for PostgreSQL
    print("Get password token.")
    token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
    conn = str(current_app.config.get('DATABASE_URI')).replace('PASSWORDORTOKEN', token.token)
    return conn
