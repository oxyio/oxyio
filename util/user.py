# Oxypanel
# File: util/user.py
# Desc: user utils

from functools import wraps
from hashlib import sha512

from sqlalchemy.orm import exc
from flask import g, abort, session, redirect
from bcrypt import hashpw, gensalt

import config
from app import app
from models.user import User
from models.permission import Permission

from .data import get_object


# Check a password
def check_password(password, hashed):
    password = sha512(password).hexdigest()
    return hashpw(password, hashed) == hashed


# Hash a password
def hash_password(password):
    password = sha512(password).hexdigest()
    return hashpw(password, gensalt(config.BCRYPT_ROUNDS))


# Get the current user object
def get_current_user():
    if hasattr(g, 'user'):
        return g.user

    session_key = session.get('session_key')
    user_id = session.get('user_id')

    # We have int key and some session key
    if not isinstance(user_id, int) or len(session_key) <= 0:
        return False

    # Find user in database
    try:
        user = User.query.filter_by(id=user_id, session_key=session_key).one()
    except exc.NoResultFound, exc.MultipleResultsFound:
        return False

    g.user = user
    return user

# Check if client logged in as user
def is_logged_in():
    if hasattr(g, 'user'):
        return True

    if get_current_user():
        return True


# Warm request permission cache
@app.before_request
def prepare_g():
    g.permissions = {}

# Check a single permission
def has_permission(permission):
    cached = g.permissions.get(permission)
    if isinstance(cached, bool):
        return cached

    if not get_current_user():
        return False

    # Keymaster? come on in!...
    if g.user.is_keymaster:
        return True

    # Check the permission w/ group
    try:
        Permission.query.filter_by(user_group_id=g.user.user_group_id, name=permission).one()
    except exc.NoResultFound, exc.MultipleResultsFound:
        g.permissions[permission] = False
        return False

    # Cache for request
    g.permissions[permission] = True
    return True

# Check multiple permissions
def has_permissions(*args):
    if all(has_permission(permission) for permission in args):
        return True


# Check permissions on single objects
def has_object_permission(module_name, object_type, object_id, permission):
    # Permission for any object
    if has_permission('{0}Any{1}{2}'.format(permission, module_name, object_type)):
        return True

    # Permission for owned objects
    if not has_permission('{0}Own{1}{2}'.format(permission, module_name, object_type)):
        return False

    # Get object, check user_id or group_id
    user = get_current_user()
    obj = get_object(module_name, object_type, object_id)
    if obj.user_id == user.id or obj.user_group_id == user.user_group_id:
        return True

def has_object_permissions(module_name, object_type, object_id, *args):
    if all(has_object_permission(module_name, object_type, permission, object_id) for permission in args):
        return True


# Check permissions against all objects
def has_own_objects_permission(module_name, objects_type, permission):
    return has_permission('{0}Own{1}{2}'.format(permission, module_name, objects_type))

def has_any_objects_permission(module_name, objects_type, permission):
    return has_permission('{0}Any{1}{2}'.format(permission, module_name, objects_type))


# Global object permission shortcuts (ie no Any or Own)
# basically: Delete<Object> or Owner<Object>
def has_global_objects_permission(module_name, objects_type, permission):
    # Permission for any object
    if has_permission('{0}{1}{2}'.format(permission, module_name, objects_type)):
        return True


# Logged in decorator (redirects to login)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect('/login')

        return f(*args, **kwargs)
    return decorated_function


# Permissions decorator (returns 403 error)
def permissions_required(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permissions(*permissions):
                return abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
