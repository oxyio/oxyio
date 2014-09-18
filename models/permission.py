# Oxypanel
# File: models/permission.py
# Desc: Permission model

from app import db


class Permission(db.Model):
    __tablename__ = 'user_permission'

    name = db.Column(db.String(64), primary_key=True)

    user_group_id = db.Column(db.Integer, db.ForeignKey('user_group.id', ondelete='CASCADE'), nullable=False)
    user_group = db.relationship('UserGroup')
