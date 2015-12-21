# oxy.io
# File: oxyio/util/password.py
# Desc: password hashing/checking

from hashlib import sha512

from bcrypt import hashpw, gensalt

from oxyio import settings


def check_password(password, hashed):
    '''Checks a password matches its hashed database value.'''

    password = sha512(password).hexdigest()
    return hashpw(password, hashed) == hashed


def hash_password(password):
    '''Turn a password into a hash.'''

    password = sha512(password).hexdigest()
    return hashpw(password, gensalt(settings.BCRYPT_ROUNDS))
