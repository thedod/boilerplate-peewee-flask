from peewee import *  # no other way to reach playhouse :(
from playhouse import flask_utils as peewee_flask_utils
from playhouse import signals as peewee_signals

database = peewee_flask_utils.FlaskDB()
