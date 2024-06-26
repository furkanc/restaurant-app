#!/bin/bash
python manage.py migrate > migrate_logs.txt 2>&1
python manage.py runserver 0.0.0.0:8000
python manage.py populate_data