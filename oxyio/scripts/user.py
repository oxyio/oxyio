# oxy.io
# File: oxyio/scripts/user.py
# Desc: create users & superusers

from boot import boot_core

from oxyio.app import db, manager
from oxyio.models.user import User


def _add_user(is_keymaster=False):
    boot_core()

    email = raw_input('# Email address: ')
    password = raw_input('# Password: ')

    user = User(email, password)
    user.is_keymaster = is_keymaster

    db.session.add(user)
    db.session.commit()

    return email


@manager.command
def add_user():
    '''Add normal users.'''

    email = _add_user()
    print '# User {0} added!'.format(email)


@manager.command
def add_keymaster():
    '''Add keymaster users (access-all-areas).'''

    email = _add_user(is_keymaster=True)
    print '# Keymaster {0} added!'.format(email)
