# oxy.io
# File: oxyio/models/base.py
# Desc: BaseObject and BaseItem
#       objects are owned by users and/or groups
#       items are owned by objects

from itertools import product

from flask import url_for
from sqlalchemy.ext.declarative import declared_attr

from oxyio.app import db
from oxyio.util.log import logger
from oxyio.web.util.request import get_request_data
from oxyio.web.util.user import (
    get_own_objects, get_object,
    has_own_objects_permission, has_object_permission
)

from .note import Note


# Maps string types -> python types
STRING_TO_PYTHON = {
    'int': int,
    'enum': set,
    'string': str
}


def _column_to_python(column):
    '''Map column types -> string_type, python_type, col args.'''

    # Integers
    if isinstance(column, db.Integer):
        return ('int', int, None)

    # Enums (which almost match db.String)
    elif isinstance(column, db.Enum):
        return ('enum', set, {value: value for value in column.enums})

    # Strings
    elif isinstance(column, db.String):
        return ('string', str, column.length)

    # Oh shit!
    else:
        logger.warning('unknown column type: {0}'.format(type(column)))


def iter_relations(relations):
    print 'ITER RELATIONS', relations
    for attribute, module_type, options in relations:
        module, object_type = module_type.split('/')
        print 'YIELD', attribute, module, object_type, options
        yield (attribute, module, object_type, options)


class Base(object):
    MODULE = OBJECT = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        super(Base, self).__init__()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Item(Base):
    _oxyio_type = 'item'

    ITEM = None

    id = db.Column(db.Integer, primary_key=True)


class Object(Base):
    _oxyio_type = 'object'

    # Config
    #

    NAME = TITLE = TITLES = None
    ES_DOCUMENTS = None # list of ES mappings
    ROUTES = None # list of (route, method, view_func, permission)

    @classmethod
    def _configure(cls):
        '''Provide defaults for the object config.'''

        # Plural title default = title+s
        if cls.TITLES is None:
            cls.TITLES = '{0}s'.format(cls.TITLE)

        if cls.ES_DOCUMENTS is None:
            cls.ES_DOCUMENTS = tuple()

        if cls.ROUTES is None:
            cls.ROUTES = tuple()

        # Generate EDIT_FIELDS, ..., LIST_MRELATIONS in order, such that the first three
        # are FIELDS, then RELATIONS, MRELATIONS and such that the methods "cascade"
        # in the order EDIT -> FILTER -> LIST
        field_attrs = [
            '_'.join((method, group))
            for group, method
            in product(
                ('FIELDS', 'RELATIONS', 'MRELATIONS'),
                ('EDIT', 'FILTER', 'LIST')
            )
        ]

        for i, attr in enumerate(field_attrs):
            # Config attr doesn't exist
            if not hasattr(cls, attr):
                new_attr = tuple()

                # If we've a previous attr, "cascade" group variables
                if i > 0:
                    previous_attr = field_attrs[i - 1]

                    # Check the previous attr is in the same group (_[FIELDS|RELATIONS])
                    if previous_attr.split('_')[1] == attr.split('_')[1]:
                        new_attr = getattr(cls, field_attrs[i - 1])

                setattr(cls, attr, new_attr)

    # Base db columns
    #

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    @declared_attr
    def user_id(self):
        return db.Column(db.Integer,
            db.ForeignKey('core_user.id', ondelete='SET NULL')
        )

    @declared_attr
    def user(self):
        return db.relationship('User')

    @declared_attr
    def user_group_id(self):
        return db.Column(db.Integer,
            db.ForeignKey('core_user_group.id', ondelete='SET NULL')
        )

    @declared_attr
    def user_group(self):
        return db.relationship('UserGroup')

    @property
    def notes(self):
        '''Lazily SELECT notes for this object.'''

        return Note.query.filter_by(
            object_id=self.id,
            object_type=self.NAME
        )

    # Exceptions
    #

    class ObjectError(Exception):
        pass

    class ValidationError(ObjectError):
        pass

    class DeletionError(ObjectError):
        pass

    # Helpers
    #

    @classmethod
    def get_column_keys(cls):
        return cls.__table__.columns.keys()

    def _col_to_data(self, field, options):
        col = self.__table__.columns.get(field)
        string_type, python_type, arg = _column_to_python(col.type)

        # Strings can be overriden into dynamic/virtual enums
        if python_type is str:
            enums = options.get('enums', None)
            if enums:
                string_type = 'enum'
                python_type = set
                arg = enums

        return string_type, python_type, arg

    def _config_to_form(self, fields):
        '''Turn device config fields into form tuples.'''

        form = []
        for field, options in fields:
            string_type, _, arg = self._col_to_data(field, options)
            form.append((string_type, field, arg, options))

        return form

    # URL Helpers
    #

    def url(self, url_string):
        return url_for(url_string,
            module_name=self.MODULE, object_type=self.OBJECT, object_id=self.id
        )

    @property
    def view_url(self):
        return self.url('view_object')

    @property
    def edit_url(self):
        return self.url('edit_object')

    @property
    def owner_url(self):
        return self.url('owner_object')

    @property
    def delete_url(self):
        return self.url('delete_object')

    # Forms
    #

    def build_filter_form(self):
        '''Builds the objects filter/search form for macro in ``function/forms.html``.'''

        # Uses just list fields
        form = self._config_to_form(self.FILTER_FIELDS)
        print 'FRM<', form
        return form

    def build_form(self):
        '''Builds an object edit/add form for macro in `function/forms.html`.'''

        # Normal edit fields + name
        form = self._config_to_form([('name', {})] + list(self.EDIT_FIELDS))

        # Check we have permission to edit the target relation or m(ulti)relation
        # append in similar format to _config_to_form
        def _do_relation(field_type, module_name, objects_type, field_name, options):
            # Do we have EditOwn permission on this type of object?
            if has_own_objects_permission(module_name, objects_type, 'edit'):
                objects = get_own_objects(module_name, objects_type)
                options['editable'] = True
            else:
                objects = getattr(self, field_name)
                options['editable'] = False

            form.append((
                field_type,
                field_name,
                objects,
                options
            ))

        # Related objects
        for field, module_name, object_type, options in iter_relations(
            self.EDIT_RELATIONS
        ):
            _do_relation(
                'relation', module_name, object_type,
                '{0}_id'.format(object_type), options
            )

        # Many/Multi-related objects
        for field, module_name, objects_type, options in iter_relations(
            self.EDIT_MRELATIONS
        ):
            options['related_ids'] = [obj.id for obj in getattr(self, field)]

            _do_relation('mrelation', module_name, objects_type, field, options)

        return form

    # Editing
    #

    def check_apply_edit_fields(self):
        '''
        Check and apply self.EDIT_FIELDS to self
        returns: status boolean, error or None
        '''
        request_data = get_request_data()

        # Check name
        name = request_data.get('name')
        if not name or len(name) <= 0:
            raise self.ValidationError('Invalid name')

        setattr(self, 'name', name)

        for field, options in self.EDIT_FIELDS:
            data = request_data.get(field)

            if data is not None:
                _, python_type, arg = self._col_to_data(field, options)

                if python_type is int:
                    try:
                        data = int(data)
                    except ValueError:
                        raise self.ValidationError('Invalid data for {0}'.format(field))

                if python_type is set:
                    if data not in arg:
                        raise self.ValidationError(
                            'Invalid data for {0}; {1} is not in set {2}'.format(
                                field, data, arg
                            )
                        )

                if python_type is str:
                    length = len(data)
                    if length > arg:
                        raise self.ValidationError(
                            'String to long for {0}, limit is {1}'.format(
                                field, arg
                            )
                        )

                # Set the value, for custom .is_valid if supplied
                setattr(self, field, data)

        # Ensure related items exist
        for field, module_name, object_type, options in iter_relations(
            self.EDIT_RELATIONS
        ):
            field_name = '{0}_id'.format(object_type)
            object_id = request_data.get(field_name)

            try:
                object_id = int(object_id)
                if object_id == 0:
                    object_id = None

            except ValueError:
                raise self.ValidationError(
                    'Invalid object_id for: {0}'.format(object_type)
                )

            # Skip if set None or no change
            if object_id is None or getattr(self, field_name) == object_id:
                continue

            # Check we even have edit permission on this object type
            if not has_object_permission(module_name, object_type, object_id, 'Edit'):
                raise self.ValidationError(
                    'You do not have permission to set {0} => {1} #{2}'.format(
                        field_name, object_type, object_id
                    )
                )

            # Set the object
            setattr(self, field_name, object_id)

        # Ensure mrelated items exist
        for field, module_name, objects_type, options in iter_relations(
            self.EDIT_MRELATIONS
        ):
            object_ids = request_data.get(field, [])

            try:
                object_ids = set([int(i) for i in object_ids])
            except ValueError:
                raise self.ValidationError(
                    'Invalid object_ids for: {0}'.format(object_type)
                )

            # Check edit permissions for each object
            if not all(
                has_object_permission(module_name, objects_type, object_id, 'Edit')
                for object_id in object_ids
            ):
                raise self.ValidationError(
                    'You do not have permission to set {0} => {1} #s: {2}'.format(
                        field, objects_type, object_ids
                    )
                )

            # Set the objects
            new_objects = [
                get_object(module_name, objects_type, obj_id)
                for obj_id in object_ids
                if obj_id > 0
            ]

            setattr(self, field, new_objects)

    # Shortcuts/misc
    #

    def serialise(self):
        '''For outputting to JSON in API-mode.'''

        return {
            key: getattr(self, key, None)
            for key in self.get_column_keys()
        }

    def delete(self):
        db.session.delete(self)

        # Find & delete any notes
        for note in self.notes:
            db.session.delete(note)

        db.session.commit()

    # Internal hooks
    #

    def is_valid(self, new=False):
        pass

    def pre_delete(self):
        pass

    def pre_view(self):
        pass

    def pre_view_edit(self):
        pass

    def post_delete(self):
        pass

    def post_edit(self):
        pass

    def post_add(self):
        pass

    # External hooks (executed in object.py & objects.py)
    #

    hooks = {
        'post_delete': [],
        'post_edit': [],
        'post_add': []
    }

    @classmethod
    def add_hook(cls, type, callback):
        '''Add hooks to apply to all object sub-classes of this'''
        cls.hooks[type].append(callback)
