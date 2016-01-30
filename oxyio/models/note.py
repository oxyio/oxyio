# oxy.io
# File: oxyio/models/note.py
# Desc: global notes model

from oxyio.app import db


class Note(db.Model):
    __tablename__ = 'core_note'

    id = db.Column(db.Integer, primary_key=True)

    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(128))

    text = db.Column(db.Text, nullable=False)
