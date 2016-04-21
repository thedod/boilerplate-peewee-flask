#!/bin/sh
echo APPLICATION_SITE_NAME=\"$SITE_NAME\" > .env
echo APPLICATION_SECRET_KEY=$(python2 randme.py) >> .env
echo APPLICATION_SECURITY_PASSWORD_SALT=$(python2 randme.py) >> .env
echo APPLICATION_DATABASE=sqlite:///dev.db >> .env
