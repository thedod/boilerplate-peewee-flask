import os
from flask import Flask, g
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from .frontend import frontend
from .nav import nav, init_custom_nav_renderer
from .db import database
from .auth import init_auth, useradmin

def stdout_logging(app):
    import sys, logging
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(stdout_handler)

def create_app(configfile=None):
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__, static_url_path='')

    # We use Flask-Appconfig here, but this is not a requirement
    AppConfig(app, configfile)

    # Kludges for heroku
    if 'DYNO' in os.environ:
        from flask_sslify import SSLify
        sslify = SSLify(app, permanent=True)
        stdout_logging(app)
        app.config['DATABASE'] = os.environ.get('DATABASE_URL')

    database.init_app(app)

    ## Note: if you remove roles, they *don't* get removed from
    # an existing datastore (flask_security doens't support that),
    # If you *really* need this, start from a fresh db.
    # USER_ROLES are hardwired in code, because without code changes
    # they're meaningless ;)
    # Also note that you don't need to explicitly mention 'admin'.
    app.config['USER_ROLES'] = ['editor']
    init_auth(app)

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True  # CDNs are cancer
    Bootstrap(app)

    init_custom_nav_renderer(app)
    nav.init_app(app)

    app.register_blueprint(frontend)
    app.register_blueprint(useradmin, url_prefix='/useradmin')

    return app
