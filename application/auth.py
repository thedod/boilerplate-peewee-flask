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
    UserMixin, RoleMixin, login_required, roles_required, current_user
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
    active = BooleanField(default=False)
    confirmed_at = DateTimeField(null=True)

    def __unicode__(self):
        return self.email

    class Meta:
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

## Forms

def _validate_on(message="Can't disable this."):
    def validator(form, field):
        if not field.data:
            # Kludge: flask_bootstrap form_field macro ignores checkbox errors.
            flash(message, "danger")
            raise validators.ValidationError(message=message)
    validator.field_flags = ('Should be on', )
    return validator

def _role_form(user, roles):
    user_roles = [ur.name for ur in user.roles]
    class RF(WtfForm):
        pass
    for r in roles:
        if r.name=='admin' and user.id==current_user.id:
            setattr(RF, r.name, BooleanField(default=r.name in user_roles,
                validators=[_validate_on(
                    message="You can't remove your own admin role.")]))
        else:    
            setattr(RF, r.name, BooleanField(default=r.name in user_roles))
    return RF

def user_form(user, roles):
    class UF(Form):
        email = EmailField(u'Email', default=user.email,
            validators=[validators.DataRequired(), validators.Email()])
        password1 = PasswordField('New password',
            validators = [
                validators.Optional(),
                validators.Length(min=10,
                    message='Password should be at least 10 characters long.')])
        password2 = PasswordField('Repeat password',
            validators = [
                validators.EqualTo('password1',
                    message="Passwords didn't match.")])
        active = BooleanField(u'Active',default=user.active,
            validators=(user.id==current_user.id and [_validate_on(
                message="You can't deactivate yourself.")] or []))
    setattr(UF, u'roles', FormField(_role_form(user, roles)))
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

@useradmin.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit(user_id):
    try:
        user = User.get(id=user_id)
    except Entry.DoesNotExist:
        abort(404)
    roles = Role.select()
    form = user_form(user, roles)(request.form)
    if form.is_submitted():
        if form.validate():
            if form.password1.data:
                user.password=encrypt_password(form.password1.data)
            form.populate_obj(user)
            user.save()
            ds=current_app.extensions['security'].datastore
            for r in roles:
                if getattr(form.roles.form, r.name).data:
                    ds.add_role_to_user(user, r.name)
                else:
                    ds.remove_role_from_user(user, r.name)
            flash('Updated user {}'.format(user.email))
            return redirect(url_for('.index'), code=303)
    else:
        form = user_form(user, roles)()
    return render_template('useradmin/edit_user.html', form=form, user=user)

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
