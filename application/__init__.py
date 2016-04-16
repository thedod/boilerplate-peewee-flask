# Welcome to the Flask-Bootstrap sample application. This will give you a
# guided tour around creating an application using Flask-Bootstrap.
#
# To run this application yourself, please install its requirements first:
#
#   $ pip install -r sample_app/requirements.txt
#
# Then, you can actually run the application.
#
#   $ flask --app=sample_app dev
#
# Afterwards, point your browser to http://localhost:5000, then check out the
# source.

from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from .frontend import frontend
from .nav import nav
from .db import database
from .auth import init_auth

def create_app(configfile=None):
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__)

    # We use Flask-Appconfig here, but this is not a requirement
    AppConfig(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    if not app.config.has_key('DATABASE') and app.config.has_key('DATABASE_URL'):
        app.config['DATABASE'] = app.config['DATABASE_URL']
    database.init_app(app)
    init_auth(app)
    Bootstrap(app)
    nav.init_app(app)
    app.register_blueprint(frontend)

    #import logging
    #from logging.handlers import WatchedFileHandler
    #@app.before_first_request
    #def setup_logging():
    #    """
    #    Setup logging
    #    """
    #    handler = WatchedFileHandler("foo.log")
    #    app.logger.addHandler(handler)
    #    app.logger.setLevel(logging.INFO)

    return app
