from flask import flash
from flask_wtf import Form
import wtforms
from wtforms import validators

class NewsItemForm(Form):
    title = wtforms.StringField('Title',
        validators=[validators.Required()])
    content = wtforms.TextAreaField('Content',
        render_kw = {"rows": 15},
        validators=[validators.Required()])
    members_only = wtforms.BooleanField()
