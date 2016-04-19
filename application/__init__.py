import os
from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from .frontend import frontend
from .nav import nav, init_custom_nav_renderer
from .db import database
from .auth import init_auth, useradmin

def stdout_logging(app):
    import sys, logging
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(stdout_handler)

def create_app(configfile=None):
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__, static_url_path='')

    # We use Flask-Appconfig here, but this is not a requirement
    AppConfig(app)
    # Kludge for heroku
    if not app.config.has_key('DATABASE'):
        app.config['DATABASE'] = os.environ.get('DATABASE_URL')
    database.init_app(app)
    init_auth(app)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    Bootstrap(app)
    init_custom_nav_renderer(app)
    nav.init_app(app)
    app.register_blueprint(frontend)
    app.register_blueprint(useradmin, url_prefix='/useradmin')
    stdout_logging(app)

    return app
