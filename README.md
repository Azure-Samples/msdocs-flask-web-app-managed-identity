# Deploy a Python (Flask) app to Azure with Managed Identity 

This Python app is a simple restaurant review application using the [Flask](https://flask.palletsprojects.com/en/2.1.x/) framework. The app uses Azure App Service, Azure Database for PostgreSQL relational database service, and Azure Storage. When deployed, Azure managed identity allows the web app hosted in App Service to connect to the database and storage resources without the need to specify sensitive connection info in code or environment variables.

This sample app can be run locally and then deployed to Azure, hosted in a fully managed Azure App Service. For more information on how to use this web app, see [Overview: Deploy a Python web app to Azure with managed identity](https://docs.microsoft.com/azure/developer/python/tutorial-python-managed-identity-01).

If you need an Azure account, you can [create on for free](https://azure.microsoft.com/free/).

A Django sample application with similar functionality is at https://github.com/Azure-Samples/msdocs-django-web-app-managed-identity.

## Requirements

The [requirements.txt](./requirements.txt) has the following packages:

| Package | Description |
| ------- | ----------- |
| [Flask](https://pypi.org/project/Flask/) | Web application framework. |
| [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) | Provides a database abstraction layer to communicate with PostgreSQL. |
| [Flask-SQLAlchemy](https://pypi.org/project/Flask-SQLAlchemy/) | Adds SQLAlchemy support to Flask application by simplifying using SQLAlchemy. Requires SQLAlchemy. |
| [Flask-Migrate](https://pypi.org/project/Flask-Migrate/) | SQLAlchemy database migrations for Flask applications using Alembic. Allows functionality parity with Django version of this sample app.|
| [pyscopg2](https://pypi.org/project/psycopg2/) | PostgreSQL database adapter for Python. |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Read key-value pairs from .env file and set them as environment variables. In this sample app, environment variables describe how to connect to the database and storage resources. Because managed identity is used no sensitive information is included in environment variables. <br><br> Flask's [dotenv support](https://flask.palletsprojects.com/en/2.1.x/cli/#environment-variables-from-dotenv) sets environment variables automatically from an `.env` file. |
| [flask_wtf](https://pypi.org/project/Flask-WTF/) | Form rendering, validation, and CSRF protection for Flask with WTForms. Uses CSRFProtect extension. |
| [azure-blob-storage](https://pypi.org/project/azure-storage/) | Microsoft Azure Storage SDK for Python |
| [azure-identity](https://pypi.org/project/azure-identity/) | Microsoft Azure Identity Library for Python |

## DefaultAzureCredential

The [DefaultAzureCredential](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential) is used in the [app.py](./app.py) file. For example:

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
blob_service_client = BlobServiceClient(
    account_url=account_url,
    credential=azure_credential)
```

The DefaultAzureCredential is also used to get a token for PostgresSQL in the [get_conn.py](./azureproject/get_conn.py) file when running in Azure.

```python
azure_credential = DefaultAzureCredential()
token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net")
conn = str(current_app.config.get('DATABASE_URI')).replace('PASSWORDORTOKEN', token.token)
```