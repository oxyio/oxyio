# Oxypanel
# File: util/user.py
# Desc: user utils

from functools import wraps
from hashlib import sha512
from urllib import quote_plus

from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import g, abort, session, redirect, request
from bcrypt import hashpw, gensalt

import config
from app import app
from models.user import User
from models.permission import Permission

from .data import get_object, get_objects, get_object_class


# Warm request permission cache
@app.before_request
def prepare_permissions_g():
    g.permissions = {}


# Get owned objects
def get_own_objects(module_name, objects_type, *filters):
    obj = get_object_class(module_name, objects_type)
    user = get_current_user()

    return get_objects(module_name, objects_type, or_(
        obj.user_id==user.id,
        obj.user_group_id==(-1 if user.user_group_id is None else user.user_group_id)
    ), *filters)


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
        return None

    # Find user in database
    try:
        user = User.query.filter_by(id=user_id, session_key=session_key).one()
    except (NoResultFound, MultipleResultsFound):
        return None

    g.user = user
    return user

# Check if client logged in as user
def is_logged_in():
    if hasattr(g, 'user'):
        return True

    if get_current_user():
        return True


# Check a single permission
def has_permission(permission):
    if not get_current_user():
        return False

    # Cache?
    cache_key = '{0}-{1}'.format(g.user.user_group_id, permission)
    cached = g.permissions.get(cache_key)
    if isinstance(cached, bool):
        return cached

    # Keymaster? come on in!...
    if g.user.is_keymaster:
        return True

    # Check the permission w/ group
    try:
        Permission.query.filter_by(user_group_id=g.user.user_group_id, name=permission).one()
    except (NoResultFound, MultipleResultsFound):
        g.permissions[cache_key] = False
        return False

    # Cache for request
    g.permissions[cache_key] = True
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
            return redirect('/login?referrer={0}'.format(quote_plus(request.url)))

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
