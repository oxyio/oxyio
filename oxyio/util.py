# oxy.io
# File: oxyio/util/util.py
# Desc: general utilities!

import hmac
from hashlib import sha512
from functools import wraps

from bcrypt import hashpw, gensalt

from oxyio import settings
from oxyio.exceptions import OxyioError


def check_password(password, hashed):
    '''
    Checks a password matches its hashed (database) value in constant time.
    '''

    password = sha512(password).hexdigest()
    return hmac.compare_digest(
        hashpw(password, hashed),
        hashed
    )


def hash_password(password):
    '''
    Turn a password into a hash.
    '''

    password = sha512(password).hexdigest()
    return hashpw(password, gensalt(settings.BCRYPT_ROUNDS))


def server_only(func):
    '''
    Decorator that prevents a function from being called in server mode.
    '''

    @wraps(func)
    def decorated(*args, **kwargs):
        if settings.BOOTED != 'web':
            raise OxyioError('{0} is only enabled in server mode'.format(func))

        return func(*args, **kwargs)
    return decorated


def worker_only(func):
    '''
    Decorator that prevents a function from being called in worker mode.
    '''
    @wraps(func)
    def decorated(*args, **kwargs):
        if settings.BOOTED != 'task':
            raise OxyioError('{0} is only enabled in worker mode'.format(func))

        return func(*args, **kwargs)
    return decorated
