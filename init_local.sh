#!/bin/sh
echo APPLICATION_SECRET_KEY=$(python2 randme.py) > .env
echo APPLICATION_SECURITY_PASSWORD_SALT=$(python2 randme.py) >> .env
cat << DATZALLFOX >> .env
APPLICATION_DATABASE=sqlite:///dev.db
APPLICATION_DEBUG_TB_INTERCEPT_REDIRECTS = False
DATZALLFOX
