#!/bin/bash -v 
pip install -r requirements.txt

flask db upgrade
