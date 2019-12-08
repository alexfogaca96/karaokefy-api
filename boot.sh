#!/bin/sh
exec gunicorn -b :5000 --chdir /home/karaokefy-api/src app:app