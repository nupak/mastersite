#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
gunicorn --workers 4 --bind 0.0.0.0:8000 scientistSite.wsgi --daemon
daphne -b 0.0.0.0 -p 8001 scientistSite.asgi:application
