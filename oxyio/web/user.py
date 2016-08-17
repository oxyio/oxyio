# oxy.io
# File: oxyio/util/web/user.py
# Desc: user utils

from functools import wraps
from urllib import quote_plus

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import g, abort, session, redirect, request

from oxyio.app import web_app
from oxyio.models.user import User, Permission
from oxyio.data import get_object, get_objects, get_object_class


# Warm request permission cache
@web_app.before_request
def prepare_permissions_g():
    g.permissions = {}


def get_current_user():
    '''Get the current user object.'''

    if hasattr(g, 'user'):
        return g.user

    session_key = session.get('session_key', '')
    user_id = session.get('user_id', None)

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


def is_logged_in():
    '''
    Test if the client is logged in as a user.
    '''

    if get_current_user():
        return True


def get_own_objects(module_name, objects_type, *filters):
    '''
    Get objects of a certain type owned by the current user.
    '''

    obj = get_object_class(module_name, objects_type)
    user = get_current_user()

    return get_objects(module_name, objects_type, obj.user_id == user.id, *filters)


def has_permission(permission):
    '''
    Check a single permission for the current user.
    '''

    if not get_current_user():
        return False

    # Cache?
    cache_key = '{0}-{1}'.format(g.user.user_group_id, permission)
    cached = g.permissions.get(cache_key)
    if isinstance(cached, bool):
        return cached

    # Check the permission w/ group
    try:
        Permission.query.filter_by(
            user_group_id=g.user.user_group_id, name=permission
        ).one()

    except (NoResultFound, MultipleResultsFound):
        g.permissions[cache_key] = False
        return False

    # Cache for request
    g.permissions[cache_key] = True
    return True


def has_permissions(*args):
    if all(has_permission(permission) for permission in args):
        return True


def has_object_permission(module_name, object_type, object_id, permission):
    '''
    Check permissions for single objects.
    '''

    object_class = get_object_class(module_name, object_type)

    if object_class.OWNABLE:
        # Permission for any object
        if has_any_objects_permission(module_name, object_type, permission):
            return True

        # Permission for owned objects
        if not has_own_objects_permission(module_name, object_type, permission):
            return False

        # Get object, check user_id or group_id
        user = get_current_user()
        obj = get_object(module_name, object_type, object_id)
        if obj and obj.user_id == user.id or obj.user_group_id == user.user_group_id:
            return True

    # Basic, un-ownable object permissions
    else:
        return has_global_objects_permission(module_name, object_type, permission)

    return False


def has_object_permissions(module_name, object_type, object_id, *args):
    if all(
        has_object_permission(module_name, object_type, permission, object_id)
        for permission in args
    ):
        return True


def has_own_objects_permission(module_name, objects_type, permission):
    '''
    Check permissions against all owned ``objects_type``.
    '''

    return has_permission('{0}Own{1}{2}'.format(permission, module_name, objects_type))


def has_any_objects_permission(module_name, objects_type, permission):
    '''
    Check permissions against all ``objects_type``.
    '''

    return has_permission('{0}Any{1}{2}'.format(permission, module_name, objects_type))


def has_global_objects_permission(module_name, objects_type, permission):
    '''
    Check permissions against global (unownable) ``objects_type``.
    '''

    if has_permission('{0}{1}{2}'.format(permission, module_name, objects_type)):
        return True


def login_required(func):
    '''
    Login decorator - redirects non-users to the login page.
    '''

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect('/login?referrer={0}'.format(quote_plus(request.url)))

        return func(*args, **kwargs)
    return decorated_function


def permissions_required(*permissions):
    '''
    Permissions decorator - redirects to login if no user or returns a 403 if the current
    user does not have permission.
    '''

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not has_permissions(*permissions):
                return abort(403)

            return func(*args, **kwargs)
        return login_required(decorated_function)
    return decorator
