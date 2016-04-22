from flask import Blueprint, render_template, flash, redirect, url_for, \
    request, redirect, current_app
import peewee
from flask_wtf import Form
import wtforms
from wtforms import validators
from wtforms.fields import html5 as wtforms_html5
from flask_security import Security, PeeweeUserDatastore, \
    UserMixin, RoleMixin, login_required, roles_required, \
    current_user, logout_user
from flask_security.utils import encrypt_password
from .db import database, peewee_flask_utils
from .forms import DeleteForm, validate_checked

## Models

class Role(database.Model, RoleMixin):
    name = peewee.CharField(unique=True)
    description = peewee.TextField(null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        order_by = ('name', )

class User(database.Model, UserMixin):
    email = peewee.CharField()
    password = peewee.CharField()
    active = peewee.BooleanField(default=True)
    confirmed_at = peewee.DateTimeField(null=True)

    def __unicode__(self):
        return self.email

    class Meta:
        db_table = 'users'  # 'user' is reserved in postgres
        order_by = ('email', )

class UserRoles(database.Model):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = peewee.ForeignKeyField(User, related_name='roles')
    role = peewee.ForeignKeyField(Role, related_name='users')
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
    class URF(wtforms.Form):
        pass
    for r in Role.select():
        if user and r.name=='admin' and user.id==current_user.id:
            setattr(URF, r.name, wtforms.BooleanField(default=r.name in user_roles,
                validators=[validate_checked(
                    message="You can't remove your own admin role.")]))
        else:
            setattr(URF, r.name, wtforms.BooleanField(default=r.name in user_roles))
    return URF

def user_form(user=None):
    class UF(Form):
        email = wtforms_html5.EmailField('Email',
            default=user and user.email or None,
            validators=[
                validators.DataRequired(),
                validators.Email(),
                _validate_user_does_not_exist(
                    exclude=user and user.email or None)])
        password1 = wtforms.PasswordField('New password',
            validators = [
                not user and validators.Required() or validators.Optional(),
                validators.Length(min=10,
                    message='Password should be at least 10 characters long.')])
        password2 = wtforms.PasswordField('Repeat password',
            validators = [
                validators.EqualTo('password1',
                    message="Passwords didn't match.")])
        # Note: by default, a new user is active
        active = wtforms.BooleanField('Active',default=not user or user.active,
            validators=(user and user.id==current_user.id and \
                [validate_checked(message="You can't deactivate yourself.")] or \
                []))
    setattr(UF, 'roles', wtforms.FormField(_user_roles_form(user)))
    return UF
 
## Views

useradmin = Blueprint('useradmin', __name__, template_folder='templates')

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
        user = peewee_flask_utils.get_object_or_404(User, User.id==user_id)
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
        flash('User {} was updated.'.format(user.email), "success")
        return redirect(url_for('.index'), code=303)
    return render_template('useradmin/create_or_edit_user.html',
        form=form, user=user)

@useradmin.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def delete_user(user_id):
    user = peewee_flask_utils.get_object_or_404(User, User.id==user_id)
    if user.id==current_user.id:
        flash("You can't delete your own user.", "danger")
        return redirect(url_for('.index'), code=303)
    form = DeleteForm(request.form)
    if form.validate_on_submit():
        user_email = user.email
        # datastore implementation is buggy. Grrr.
        # current_app.extensions['security'].datastore.delete_user(user)
        # Let's do it by hand
        user.delete_instance(recursive=True)
        flash("User {} was deleted.".format(user_email), "success")
        return redirect(url_for('.index'), code=303)
    return render_template('useradmin/delete_user.html',
        form=form, user=user)

## App init

def init_auth(app):
    user_datastore = PeeweeUserDatastore(database, User, Role, UserRoles)
    security = Security(app, user_datastore)
    app.before_first_request(lambda: _init_auth_datastore(user_datastore))

def _init_auth_datastore(datastore):
    # If it's a fresh database, create an initial admin user.
    if not User.table_exists():
        for Model in (User, Role, UserRoles):
            Model.create_table(fail_silently=True)
        initial_admin_email = 'youshould@change.me'
        from random import _urandom
        initial_admin_password = \
            _urandom(12).encode('base-64')[:-2]
        admin_user = datastore.create_user(
            email=initial_admin_email,
            password=encrypt_password(initial_admin_password),
            active=True)
        admin_role = datastore.create_role(name='admin')
        flash("""Fresh installation: Login as "{}" with password "{}",
and change your email and password via the user admin interface.
This message only appears once!""".format(
            initial_admin_email, initial_admin_password), "danger")
        datastore.add_role_to_user(admin_user, admin_role)
        logout_user() # in case there's a stale cookie

    # This is *always* done (in case new roles were added)
    # Heads up: USER_ROLES are hard-coded at __init__.py
    for role_name in current_app.config['USER_ROLES']:
        if not datastore.find_role(role_name):
            datastore.create_role(name=role_name)
