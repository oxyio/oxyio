# Oxypanel
# File: models/meta.py
# Desc: the meta base for all SQLAlchemy models to auto-add to object/item maps
#       sadly, this requires some imports-in-functions, as app needs to load
#       this file to create the SQLAlchemy instance with this meta class

from sqlalchemy.ext.declarative import DeclarativeMeta

from ..util.log import logger


# Meta baseclass which applies to objects & items
class BaseMeta(DeclarativeMeta):
    def __init__(cls, name, bases, d):
        if hasattr(cls, '_type'):
            from ..app import object_map, item_map # see top

            # Auto-generate table names
            if not hasattr(cls, '__tablename__'):
                cls.__tablename__ = cls.NAME.replace('/', '_')

            # Objects
            if cls._type == 'object':
                # Plural title default = title+s
                if cls.TITLES is None:
                    cls.TITLES = '{0}s'.format(cls.TITLE)

                module_name, object_name = cls.NAME.split('/')
                object_map[module_name][object_name] = cls
                logger.debug('Registered object {}/{}'.format(module_name, object_name))

            # Items
            elif cls._type == 'item':
                module_name, object_name, item_name = cls.NAME.split('/')

                if not item_map[module_name].get(object_name):
                    item_map[module_name][object_name] = {}

                item_map[module_name][object_name][item_name] = cls
                logger.debug('Registered item {}/{}'.format(module_name, item_name))

        super(BaseMeta, cls).__init__(name, bases, d)
