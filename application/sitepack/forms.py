from flask import flash
from flask_wtf import Form
import wtforms
from wtforms import validators
from flask_babel import gettext as _, lazy_gettext

## validators

def validate_checked(message="Can't disable this."):
    def validator(form, field):
        if not field.data:
            # Kludge: flask_bootstrap form_field macro ignores checkbox errors.
            flash(message, "danger")
            raise validators.ValidationError(message)
    return validator

## Forms

class DeleteForm(Form):
    confirmation = wtforms.BooleanField(lazy_gettext("I know what I'm doing."),
        validators=[validate_checked(
            message=lazy_gettext("You have to know what you're doing."))])
    submit = wtforms.SubmitField(lazy_gettext("Delete"))
