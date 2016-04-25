# -*- coding: utf-8 -*-
# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, flash, redirect, g, \
    current_app
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_security import login_required, roles_required, current_user
from flask_babel import gettext as _

from sitepack.nav import nav, ExtendedNavbar, LocalizedView
from sitepack.db import peewee_flask_utils
from sitepack.babel_by_url import babel_config, get_language_code
from .models import NewsItem

frontend = Blueprint('frontend', __name__)

def frontend_top_nav():
        navbar = ExtendedNavbar(
            LocalizedView(babel_config('SITE_TITLE'), 'frontend.index'),
            root_class='navbar navbar-inverse navbar-fixed-top',
            items = (
                LocalizedView(_('Home'), 'frontend.index'),
                LocalizedView(_('Members'), 'frontend.members'),
            )
        )
        if current_user.is_active:
            navbar.right_items = (
                Text('{}:'.format(current_user.email)),
                LocalizedView(_('Logout'), 'security.logout'),
                LocalizedView(_('Change password'), 'security.change_password'),
            )
            if current_user.has_role('editor'):
                navbar.right_items += \
                    (LocalizedView(_('Site editor'), 'backend.index'),)
            if current_user.has_role('admin'):
                navbar.right_items += \
                    (LocalizedView(_('User admin'), 'useradmin.index'),)
        else:
            navbar.right_items = ( View(_('Login'), 'security.login'), )

        if get_language_code()=='en':
            navbar.right_items += (
                LocalizedView(u'עברית', 'frontend.index', 'he'), )
        else:
            navbar.right_items += (
                LocalizedView('English', 'frontend.index', 'en'), )
        return navbar

nav.register_element('frontend_top', frontend_top_nav)

@frontend.route('/')
def index(page=None):
    return peewee_flask_utils.object_list('index.html',
        query=NewsItem.select().where(NewsItem.members_only==False),
        check_bounds=False,  # we don't want 404 if empty
        paginate_by=current_app.config['FRONTEND_ITEMS_PER_PAGE'])

@frontend.route('/members')
@login_required
def members(page=None):
    return peewee_flask_utils.object_list('members.html',
        query=NewsItem.select().where(NewsItem.members_only==True),
        check_bounds=False,  # we don't want 404 if empty
        paginate_by=current_app.config['FRONTEND_ITEMS_PER_PAGE'])
