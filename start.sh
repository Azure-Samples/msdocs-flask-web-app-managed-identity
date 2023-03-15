#!/bin/bash -v 
pip install -r requirements.txt

flask db upgrade

gunicorn --workers 2 --threads 4 --timeout 60 --access-logfile '-' --error-logfile '-' --bind=0.0.0.0:5000 --chdir=/home/site/wwwroot app:app