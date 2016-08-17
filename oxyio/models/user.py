# oxy.io
# File: oxyio/models/user.py
# Desc: User, UserGroup and Permission models

from hashlib import md5

from oxyio.app import db
from oxyio.util import hash_password


class UserGroup(db.Model):
    __tablename__ = 'core_user_group'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), nullable=False)

    def __init__(self, name):
        self.name = name


class Permission(db.Model):
    __tablename__ = 'core_user_permission'

    name = db.Column(db.String(64), primary_key=True)

    user_group_id = db.Column(db.Integer,
        db.ForeignKey('core_user_group.id', ondelete='CASCADE'),
        nullable=False, primary_key=True
    )
    user_group = db.relationship('UserGroup')

    def __init__(self, name, user_group_id):
        self.name = name
        self.user_group_id = user_group_id


class User(db.Model):
    __tablename__ = 'core_user'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)

    password = db.Column(db.String(128))
    session_key = db.Column(db.String(128))
    # For resetting passwords
    reset_key = db.Column(db.String(128))
    reset_time = db.Column(db.DateTime)

    user_group_id = db.Column(db.Integer,
        db.ForeignKey('core_user_group.id', ondelete='SET NULL')
    )
    user_group = db.relationship('UserGroup', backref=db.backref('users'))

    @property
    def gravatar(self):
        return 'http://www.gravatar.com/avatar/{0}?s=40&d=retro'.format(
            md5(self.email).hexdigest()
        )

    def __init__(self, email, password=None, name=None):
        self.email = email

        if password is not None:
            self.password = hash_password(password)

        if name is None:
            self.name = email
        else:
            self.name = name
