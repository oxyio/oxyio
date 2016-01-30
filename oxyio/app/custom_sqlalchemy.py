# oxy.io
# File: app/custom_sqlalchemy.py
# Desc: A custom flask-sqlalchemy class overriding the original's make_declarative_base
#       this allows us to use our own. There was a PR but none of the projects maintainers
#       left any comments/feedback so I gave up and simply created this override.

from sqlalchemy.ext.declarative import declarative_base
from flask.ext.sqlalchemy import (
    _QueryProperty, Model,
    SQLAlchemy as OriginalSQLAlchemy
)


class SQLAlchemy(OriginalSQLAlchemy):
    def make_declarative_base(self):
        '''Creates oxyio's custom declarative base.'''

        # Unfortunately we have to nest this import as the file imports from oxyio.app,
        # which also imports this file.
        from oxyio.models.base import BaseMeta

        base = declarative_base(cls=Model, name='Model', metaclass=BaseMeta)
        base.query = _QueryProperty(self)
        base.db = self

        return base
