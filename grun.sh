#!/bin/sh
cd "$(dirname "$0")"
source "venv/bin/activate"
env $(cat ".env") gunicorn --worker-class gevent --log-file=- -w 3 "application:create_app()"
