#!/bin/bash -v 
pip install -r requirements.txt

export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')

flask db upgrade

gunicorn --bind=0.0.0.0:8000 --timeout 120 app:app