# Oxypanel
# File: models/user.py
# Desc: User, UserGroup and Permission models

from hashlib import md5

from ..app import db


class UserGroup(db.Model):
    __tablename__ = 'user_group'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), nullable=False)

    def __init__(self, name):
        self.name = name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)

    password = db.Column(db.String(128))
    session_key = db.Column(db.String(128))
    # For resetting passwords
    reset_key = db.Column(db.String(128))
    reset_time = db.Column(db.DateTime)

    # Have all permissions
    is_keymaster = db.Column(db.Boolean, nullable=False, default=False, server_default='0')

    user_group_id = db.Column(db.Integer, db.ForeignKey('user_group.id', ondelete='SET NULL'))
    user_group = db.relationship('UserGroup', backref=db.backref('users'))

    @property
    def gravatar(self):
        return 'http://www.gravatar.com/avatar/{0}?s=40&d=retro'.format(md5(self.email).hexdigest())

    def __init__(self, email, password=None, name=None):
        self.email = email

        if password is not None:
            from util.web.user import hash_password # prevent circular import
            self.password = hash_password(password)

        if name is None:
            self.name = email
        else:
            self.name = name