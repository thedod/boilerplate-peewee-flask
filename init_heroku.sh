#!/bin/sh
heroku config:set APPLICATION_SECRET_KEY=$(python2 randme.py)
heroku config:set APPLICATION_SECURITY_PASSWORD_SALT=$(python2 randme.py)
