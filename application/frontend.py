# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_security import login_required, current_user
from markupsafe import escape

from .forms import SignupForm
from .nav import nav

frontend = Blueprint('frontend', __name__)


# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
def frontend_top_nav():
        menu = [
            View('Boilerplate App', 'frontend.index'),
            View('Home', 'frontend.index'),
            View('Forms Example', 'frontend.example_form'),
            View('Members', 'frontend.members'),
            #This screws gunicorn
            #View('Debug-Info', 'debug.debug_root'),
            Subgroup(
                'Docs',
                Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
                Link('Flask-AppConfig', 'https://github.com/mbr/flask-appconfig'),
                Link('Flask-Debug', 'https://github.com/mbr/flask-debug'),
                Separator(),
                Text('Bootstrap'),
                Link('Getting started', 'http://getbootstrap.com/getting-started/'),
                Link('CSS', 'http://getbootstrap.com/css/'),
                Link('Components', 'http://getbootstrap.com/components/'),
                Link('Javascript', 'http://getbootstrap.com/javascript/'),
                Link('Customize', 'http://getbootstrap.com/customize/'),
            )
        ]
        if current_user.is_active:
            menu.append(View('Logout {}'.format(current_user.email), 'security.logout'))
            menu.append(View('Change password', 'security.change_password'))
        else:
            menu.append(View('Login', 'security.login'))
        return Navbar(*menu)

nav.register_element('frontend_top', frontend_top_nav)

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@frontend.route('/')
def index():
    return render_template('index.html')

@frontend.route('/members')
@login_required
def members():
    return render_template('members.html')

# Shows a long signup form, demonstrating form rendering.
@frontend.route('/example-form/', methods=('GET', 'POST'))
def example_form():
    form = SignupForm()

    if form.validate_on_submit():
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        flash('Hello, {}. You have successfully signed up'
              .format(escape(form.name.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('frontend.index'))

    return render_template('signup.html', form=form)
