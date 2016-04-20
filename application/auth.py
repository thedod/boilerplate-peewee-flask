from flask import Blueprint, render_template, flash, redirect, url_for, \
    request, abort, redirect, current_app, flash
from peewee import *
from flask_wtf import Form
from wtforms import Form as WtfForm, StringField, PasswordField, \
    BooleanField, FormField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from wtfpeewee.orm import model_form
from flask_security import Security, PeeweeUserDatastore, \
    UserMixin, RoleMixin, login_required, roles_required, \
    current_user
from flask_security.utils import encrypt_password
from .db import database

## Models

class Role(database.Model, RoleMixin):
    name = CharField(unique=True)
    description = TextField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        order_by = ('name', )

class User(database.Model, UserMixin):
    email = CharField()
    password = CharField()
    # Peewee seems to have a problem with Booleanfield.
    # At the moment active is a property. Checking this...
    _activint = IntegerField(default=1)
    confirmed_at = DateTimeField(null=True)

    @property
    def active(self):
        return self._activint!=0

    @active.setter
    def active(self, value):
        self._activint = value and 1 or 0

    def __unicode__(self):
        return self.email

    class Meta:
        db_table = 'users'  # 'user' is reserved in postgres
        order_by = ('email', )

class UserRoles(database.Model):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)

    def __unicode__(self):
        return u'{}({})'.format(self.role,self.user)

    class Meta:
        indexes = (
            (('user', 'role'), True),
        )
        order_by = ('user', 'role')

## Validators

def _validate_on(message="Can't disable this."):
    def validator(form, field):
        if not field.data:
            # Kludge: flask_bootstrap form_field macro ignores checkbox errors.
            flash(message, "danger")
            raise validators.ValidationError(message)
    return validator

def _validate_user_does_not_exist(exclude=None):
    def validator(form, field):
        if field.data!=exclude and \
            current_app.extensions['security'].datastore.find_user(email=field.data):
            raise validators.ValidationError(
                "User {} is already registered".format(field.data))
    return validator

## Forms

def _user_roles_form(user=None):
    user_roles = user and [ur.name for ur in user.roles] or []
    class URF(WtfForm):
        pass
    for r in Role.select():
        if user and r.name=='admin' and user.id==current_user.id:
            setattr(URF, r.name, BooleanField(default=r.name in user_roles,
                validators=[_validate_on(
                    message="You can't remove your own admin role.")]))
        else:
            setattr(URF, r.name, BooleanField(default=r.name in user_roles))
    return URF

def user_form(user=None):
    class UF(Form):
        email = EmailField(u'Email', default=user and user.email or None,
            validators=[
                validators.DataRequired(),
                validators.Email(),
                _validate_user_does_not_exist(
                    exclude=user and user.email or None)])
        password1 = PasswordField('New password',
            validators = [
                not user and validators.Required() or validators.Optional(),
                validators.Length(min=10,
                    message='Password should be at least 10 characters long.')])
        password2 = PasswordField('Repeat password',
            validators = [
                validators.EqualTo('password1',
                    message="Passwords didn't match.")])
        # Note: by default, a new user is active
        active = BooleanField(u'Active',default=not user or user.active,
            validators=(user and user.id==current_user.id and \
                [_validate_on(message="You can't deactivate yourself.")] or \
                []))
    setattr(UF, u'roles', FormField(_user_roles_form(user)))
    return UF
 
## Views

useradmin = Blueprint('useradmin', __name__)

@useradmin.route('/')
@login_required
@roles_required('admin')
def index():
    users = User.select()
    roles = Role.select()
    user_roles = dict([(u,[r.name for r in u.roles]) for u in users])
    return render_template('useradmin/index.html',
        users=users, roles=roles, user_roles=user_roles)

@useradmin.route('/create_user', methods=['GET', 'POST'])
@useradmin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def create_or_edit_user(user_id=None):
    if user_id:
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404)
    else:
        user = None  # Create a new user
    form = user_form(user)(request.form)
    if form.validate_on_submit():
        ds = current_app.extensions['security'].datastore
        if user:
            if form.password1.data:
                user.password=encrypt_password(form.password1.data)
            form.populate_obj(user)
            user.save()
        else:
            user = ds.create_user(
                email=form.email.data,
                password=encrypt_password(form.password1.data),
                active=form.active.data)
        for r in Role.select():
            if getattr(form.roles.form, r.name).data:
                ds.add_role_to_user(user, r.name)
            else:
                ds.remove_role_from_user(user, r.name)
        flash('Updated user {}'.format(user.email))
        return redirect(url_for('.index'), code=303)
    return render_template('useradmin/create_or_edit_user.html', form=form, user=user)

## App init

def init_auth(app):
    user_datastore = PeeweeUserDatastore(database, User, Role, UserRoles)
    security = Security(app, user_datastore)
    app.before_first_request(lambda: _init_auth_datastore(user_datastore))

def _init_auth_datastore(datastore):
    if not User.table_exists():
        for Model in (User, Role, UserRoles):
            Model.create_table(fail_silently=True)
        admin_user = datastore.create_user(
            email='youshould@change.me',
            password=encrypt_password('YouShouldChangeThisPassword!!1'),
            active=True)
        admin_role = datastore.create_role(name='admin')
        datastore.add_role_to_user(admin_user, admin_role)
        datastore.create_role(name='staff')
