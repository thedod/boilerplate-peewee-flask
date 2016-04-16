from peewee import *
from flask.ext.security import Security, PeeweeUserDatastore, \
    UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password
from .db import database

class Role(database.Model, RoleMixin):
    name = CharField(unique=True)
    description = TextField(null=True)

class User(database.Model, UserMixin):
    email = TextField()
    password = TextField()
    active = BooleanField(default=True)
    confirmed_at = DateTimeField(null=True)

class UserRoles(database.Model):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)

def init_auth(app):
    user_datastore = PeeweeUserDatastore(database, User, Role, UserRoles)
    security = Security(app, user_datastore)
    app.before_first_request(lambda: _init_auth_datastore(user_datastore))

def _init_auth_datastore(datastore):
    if not User.table_exists():
        for Model in (User, Role, UserRoles):
            Model.create_table(fail_silently=True)
        datastore.create_user(email='admin@whowantsto.no', password=encrypt_password('changeme'))
