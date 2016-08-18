# oxy.io
# File: oxyio/scripts/user.py
# Desc: create users & superusers

from oxyio.app import db, manager
from oxyio.models.user import User


@manager.command
def add_user():
    '''
    Add users.
    '''

    email = raw_input('# Email address: ')
    password = raw_input('# Password: ')

    user = User(email, password)

    db.session.add(user)
    db.session.commit()

    print '# User {0} added!'.format(email)
