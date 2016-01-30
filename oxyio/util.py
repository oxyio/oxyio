# oxy.io
# File: oxyio/util/util.py
# Desc: general utilities!

from hashlib import sha512

from bcrypt import hashpw, gensalt

from oxyio import settings


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
