# oxy.io
# File: oxyio/models/item.py
# Desc: the base Item model

from sqlalchemy import event

from oxyio.app import db

from .base import Base


class Item(Base):
    '''``Item``s are nested/owned by an ``Object``.'''

    _oxyio_type = 'item'

    ITEM = None

    # False = no object linking (default)
    # True = link any object
    # tuple of object strings = link only this type of object
    MULTI_OBJECT = False

    id = db.Column(db.Integer, primary_key=True)


def test(*args, **kwargs):
    print 'TEST', args, kwargs


event.listen(Item, 'before_insert', test)
