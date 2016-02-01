# oxy.io
# File: oxyio/util/util.py
# Desc: general utilities!

from hashlib import sha512
from functools import wraps

from bcrypt import hashpw, gensalt

from oxyio import settings
from oxyio.exceptions import OxyioError


def check_password(password, hashed):
    '''Checks a password matches its hashed (database) value.'''

    password = sha512(password).hexdigest()
    return hashpw(password, hashed) == hashed


def hash_password(password):
    '''Turn a password into a hash.'''

    password = sha512(password).hexdigest()
    return hashpw(password, gensalt(settings.BCRYPT_ROUNDS))


def since_datetime(since):
    '''Parses human time deltas (1m, 1h, 1d, 1w, etc) and returns now - that.'''

    pass


def server_only(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if settings.BOOTED != 'web':
            raise OxyioError('{0} is only enabled in server mode'.format(func))

        return func(*args, **kwargs)
    return decorated


def worker_only(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if settings.BOOTED != 'task':
            raise OxyioError('{0} is only enabled in worker mode'.format(func))

        return func(*args, **kwargs)
    return decorated
