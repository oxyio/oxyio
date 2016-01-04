# oxy.io
# File: oxyio/models/base.py
# Desc: BaseObject and BaseItem
#       objects are owned by users and/or groups
#       items are owned by objects

from sqlalchemy.ext.declarative import DeclarativeMeta

from oxyio.app import object_map, item_map
from oxyio.util.log import logger


class BaseMeta(DeclarativeMeta):
    '''
    Meta baseclass which applies to objects & items, and registers them on
    ``oxyio.app.[module_map|object_map]`` Note this is applied by Flask-SQLAlchemy, not
    __metaclass__ing below.
    '''

    def __init__(cls, name, bases, d):
        if hasattr(cls, '_oxyio_type'):
            # Auto-generate table names
            if not hasattr(cls, '__tablename__'):
                cls.__tablename__ = cls.NAME.replace('/', '_')

            # Objects
            if cls._oxyio_type == 'object':
                # Configure object config defaults
                cls._configure()

                # Map the object
                module_name, object_name = cls.NAME.split('/')
                object_map[module_name][object_name] = cls

                # Attach split names back on the object
                cls.MODULE = module_name
                cls.OBJECT = object_name

                logger.debug('Registered object {0}/{1}'.format(
                    module_name, object_name
                ))

            # Items
            elif cls._oxyio_type == 'item':
                module_name, object_name, item_name = cls.NAME.split('/')

                # Map the item
                if not item_map[module_name].get(object_name):
                    item_map[module_name][object_name] = {}

                item_map[module_name][object_name][item_name] = cls

                # Attach split names back on the object
                cls.MODULE = module_name
                cls.OBJECT = object_name
                cls.ITEM = item_name

                logger.debug('Registered item {0}/{1}/{2}'.format(
                    module_name, object_name, item_name
                ))

        super(BaseMeta, cls).__init__(name, bases, d)
