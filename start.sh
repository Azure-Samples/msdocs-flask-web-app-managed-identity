#!/bin/bash -v 
pip install -r requirements.txt

flask db upgrade

gunicorn --bind=0.0.0.0:5000 --timeout 120 app:app