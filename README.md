### A Peewee+Flask_Security Boilerplate App

#### [Demo](https://boilerplate-peewee-flask.herokuapp.com)

This is my [Flask](http://flask.pocoo.org) /
[Peewee](http://peewee.readthedocs.org) /
[Flask-Security](https://pythonhosted.org/Flask-Security) /
[Flask-Bootstrap](http://pythonhosted.org/Flask-Bootstrap)
"hello, world" du jour.

#### Why?

[Flask-Peewee](http://flask-peewee.readthedocs.org/en/latest/) used to be a
simple way to whip up a site with user management and object admin, but it froze
in maintenance-only mode, and it doesn't play nice with
[application factories](http://flask.pocoo.org/docs/0.10/patterns/appfactories/).

The playhouse's
[flask_utils](http://peewee.readthedocs.org/en/latest/peewee/playhouse.html#flask-utils)
provides smoother flask integration.
As [recommended](https://archive.is/H6ccV#selection-72.3-85.14), I've chosen
[Flask-Security](https://pythonhosted.org/Flask-Security/) for auth, and admin
I can live without.

#### To initialize

```
virtualenv -p python2 venv
source venv/bin/activate
pip install -r requirements-local.txt
```

**Heads up:** `requirements.txt` contains Heroku-specific stuff
(and doesn't contain debug goodies).

#### To run locally

`./init_local.sh` creates the `.env` you need, then `./rundev.sh` runs a web
server (with a debug toolbar) on port `5000`.

#### To deploy at Heroku

```
heroku create
heroku addons:create heroku-postgresql:hobby-dev
./init_heroku.sh
git push heroku master
heroku open
```

#### Structure

Everyting is under `application/`. Stuff that *isn't* app-specific is under
`application/sitepack/`.

Stuff directly under `application/` is the
[demo app](https://boilerplate-peewee-flask.herokuapp.com) and you'd probably want to
rewrite most of it, but note that `application/templates/security` and
`application/sitepack/templates/base.html` are symlinks (from `application/`
to `sitepack/` and back), so if you move things around, remember to update them.

`application/default_config.py` contains settings that assume you don't want
SMTP (this is intended for inhouse apps, where users don't register via web, but
rather ask an admin for an account).
See below how to enable Flask-Security's mail-related features.

#### User roles

You can only configure roles at `application/__init__.py` (config options ares
ignored, since roles are meaningless unless there's code that uses them).
The example app comes with `['editor']` (`'admin'` is hardwired and you don't
need to declare it explicitly).

**Note:** you can *add* roles, but if you *delete* one, it *doesn't* get deleted
from an existing database (that's a Flask-Security "feature").
You'll need to either reset the database, or perform "sql surgery" on the
existing one in order to do that.

Tl;dr &mdash; if you don't want the `'editor'` role, remove it *before* you
run your app (you can always add it later if you change your mind).

#### Initial admin user

First time you access the app via web, it initializes the auth tables and
flashes a message like this (with some *other* random password, of course):

![fresh installation flash message](https://lut.im/kDL4rN1Hkd/HkEByyVOfsHS4pDu.jpg)

If you accidentally refresh the page before copy/pasting the password,
**you'll need to reset your database** (or at least drop the `users` table).

#### Enabling SMTP-related features

If you use [Mailgun](https://elements.heroku.com/addons/mailgun)
or [SendGrid](https://elements.heroku.com/addons/sendgrid)
Heroku SMTP addons,
[flask-appconfig](https://pypi.python.org/pypi/flask-appconfig)
will automagically configure your app's
[Flask-Mail](http://pythonhosted.org/Flask-Mail/) and you can enable
`SECURITY_REGISTERABLE` and `SECURITY_RECOVERABLE` right away
(with other SMTP solutions, you'll need to configure it via environment
variables / `heroku config:set`).

To enable `SECURITY_CONFIRMABLE`, you should *first* login as the initial admin,
and change to an email address **you can receive mail at**.
Once you enable `SECURITY_CONFIRMABLE`, you should send yourself a
confirmation email via `/auth/confirm`, and click on the activation link you
receive, before you can login again.

`SECURITY_PASSWORDLESS` and `SECURITY_TRACKABLE` are not supported, but should
be pretty easy to support.
