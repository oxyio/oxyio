# oxy.io
# File: oxyio/models/base.py
# Desc: BaseObject and BaseItem
#       objects are owned by users and/or groups
#       items are owned by objects

from itertools import product

from flask import url_for
from sqlalchemy.ext.declarative import declared_attr

from oxyio.app import db
from oxyio.log import logger
from oxyio.util import server_only
from oxyio.exceptions import OxyioError
from oxyio.stats import index_object_stats
from oxyio.data import get_object_class

from oxyio.web.user import (
    get_own_objects, get_objects, get_object, has_object_permission,
    has_any_objects_permission, has_own_objects_permission, has_global_objects_permission,
)

from .base import Base
from .note import Note


# Maps string types -> python types
STRING_TO_PYTHON = {
    'int': int,
    'enum': set,
    'string': str,
}


def _column_to_python(column):
    '''
    Map column types -> string_type, python_type, col args.
    '''

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
    for attribute, module_type, options in relations:
        module, object_type = module_type.split('/')
        yield (attribute, module, object_type, options)


class Object(Base):
    _oxyio_type = 'object'

    # Config
    #

    NAME = TITLE = TITLES = None

    # Whether this object can be owned by users
    OWNABLE = False

    # Whether this object can be added manually
    ADDABLE = True

    # List of ES mappings for this object
    ES_DOCUMENTS = None

    # Routes for this object - list of (route, method, view_func, permission)
    ROUTES = None

    @classmethod
    def _configure(cls):
        '''
        Provide defaults for the object config.
        '''

        # Plural title default = title+s
        if cls.TITLES is None:
            cls.TITLES = '{0}s'.format(cls.TITLE)

        if cls.ES_DOCUMENTS is None:
            cls.ES_DOCUMENTS = ()

        if cls.ROUTES is None:
            cls.ROUTES = ()

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
                new_attr = ()

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
        if self.OWNABLE:
            return db.Column(db.Integer,
                db.ForeignKey('core_user.id', ondelete='SET NULL')
            )

    @declared_attr
    def user(self):
        if self.OWNABLE:
            return db.relationship('User')

    @property
    def notes(self):
        '''
        Lazily SELECT notes for this object.
        '''

        return Note.query.filter_by(
            object_id=self.id,
            object_type=self.NAME
        )

    # Exceptions
    #

    class ObjectError(OxyioError):
        pass

    class EditRequestError(ObjectError):
        pass

    class ValidationError(ObjectError):
        pass

    class DeletionError(ObjectError):
        pass

    # Internal Helpers
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
        '''
        Turn device config fields into form tuples.
        '''

        form = []

        for field, options in fields:
            string_type, _, arg = self._col_to_data(field, options)
            form.append((string_type, field, arg, options))

        return form

    @server_only
    def _do_form_relation(self, field_type, module_name, objects_type, field_name, options):
        '''
        Check we have permission to edit the target relation or m(ulti)relation append in
        similar format to _config_to_form
        '''

        object_class = get_object_class(module_name, objects_type)

        # Do we have edit permissions on this type of object
        if object_class.OWNABLE:
            # Edit any object
            if has_any_objects_permission(module_name, objects_type, 'edit'):
                objects = get_objects(module_name, objects_type)

            # Edit just our own objcts
            elif has_own_objects_permission(module_name, objects_type, 'edit'):
                objects = get_own_objects(module_name, objects_type)

        # Non-owned object, check global permission
        elif has_global_objects_permission(module_name, objects_type, 'edit'):
            objects = get_objects(module_name, objects_type)

        # The current user does not have permission to edit either their own or all
        # related objects, so we don't add this field to the form at all.
        else:
            objects = (
                [getattr(self, field_name)]
                if field_type == 'relation'
                else getattr(self, field_name)
            )
            options['editable'] = False

        field_id_name = (
            '{0}_id'.format(field_name)
            if field_type == 'relation'
            else '{0}_ids'.format(field_name)
        )

        return (
            field_type,
            field_id_name,
            objects,
            options,
        )

    # Public Helpers
    #

    def url(self, url_string):
        return url_for(
            '{0}.{1}_{2}'.format(self.MODULE, url_string, self.OBJECT),
            object_id=self.id
        )

    @property
    def view_url(self):
        return self.url('view')

    @property
    def edit_url(self):
        return self.url('edit')

    @property
    def owner_url(self):
        return self.url('owner')

    @property
    def delete_url(self):
        return self.url('delete')

    def index_stats(self, *args, **kwargs):
        index_object_stats(self, *args, **kwargs)

    # Forms
    #

    @server_only
    def build_filter_form(self):
        '''
        Builds the objects filter/search form for macro in ``function/forms.html``.
        '''

        form = self._config_to_form([('name', {})] + list(self.FILTER_FIELDS))

        for field, module_name, object_type, options in iter_relations(
            self.FILTER_RELATIONS
        ):
            form.append(self._do_form_relation(
                'relation', module_name, object_type,
                field, options,
            ))

        for field, module_name, objects_type, options in iter_relations(
            self.FILTER_MRELATIONS
        ):
            form.append(self._do_form_relation(
                'relation', module_name, objects_type,
                field, options,
            ))

        return form

    @server_only
    def build_form(self):
        '''
        Builds an object edit/add form for macro in ``function/forms.html``.
        '''

        # Normal edit fields + name
        form = self._config_to_form([('name', {})] + list(self.EDIT_FIELDS))

        # Related objects
        for field, module_name, object_type, options in iter_relations(
            self.EDIT_RELATIONS
        ):
            form.append(self._do_form_relation(
                'relation', module_name, object_type,
                field, options,
            ))

        # Many/Multi-related objects
        for field, module_name, objects_type, options in iter_relations(
            self.EDIT_MRELATIONS
        ):
            options['related_ids'] = [obj.id for obj in getattr(self, field)]
            form.append(self._do_form_relation(
                'mrelation', module_name, objects_type,
                field, options
            ))

        return form

    # Editing
    #

    @server_only
    def edit(self, request_data):
        self.check_apply_edit_fields(request_data)
        self.check_apply_edit(request_data)

    @server_only
    def check_apply_edit(self, request_data):
        '''
        Custom check/apply request data for fields not in ``self.EDIT_FIELDS``.
        '''
        pass

    @server_only
    def check_apply_edit_fields(self, request_data):
        '''
        Check and apply ``self.EDIT_FIELDS`` to ``self``.

        Raises:
            ``self.EditRequestError``
        '''

        # Name field present on all objects
        name = request_data.get('name')
        if name is not None:
            # Catch empty names
            if not name:
                raise self.EditRequestError('Invalid name')

            setattr(self, 'name', name)

        # Ensure configured request fields are correct
        for field, options in self.EDIT_FIELDS:
            data = request_data.get(field)

            # Skip if not provided (partial update)
            if data is None:
                continue

            _, python_type, arg = self._col_to_data(field, options)

            if python_type is int:
                try:
                    data = int(data)
                except ValueError:
                    raise self.EditRequestError('Invalid data for {0}'.format(field))

            if python_type is set:
                if data not in arg:
                    raise self.EditRequestError(
                        'Invalid data for {0}; {1} is not in set {2}'.format(
                            field, data, arg
                        )
                    )

            if python_type is str:
                length = len(data)
                if length > arg:
                    raise self.EditRequestError(
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
            field_name = '{0}_id'.format(field)
            object_id = request_data.get(field_name)

            # Skip if not provided (partial update)
            if object_id is None:
                continue

            try:
                object_id = int(object_id)
                if object_id == 0:
                    object_id = None

            except ValueError:
                raise self.EditRequestError(
                    'Invalid object_id for: {0}'.format(object_type)
                )

            # Check we even have edit permission on this object type
            if (
                object_id is not None
                and not has_object_permission(module_name, object_type, object_id, 'edit')
            ):
                raise self.EditRequestError(
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
            field_name = '{0}_ids'.format(field)
            object_ids = request_data.get(field_name)

            # Skip if not provided (partial update)
            if object_ids is None:
                continue

            try:
                object_ids = set([int(i) for i in object_ids])

            except ValueError:
                raise self.EditRequestError(
                    'Invalid object_ids for: {0}'.format(object_type)
                )

            # Check edit permissions for each object
            if not all(
                has_object_permission(module_name, objects_type, object_id, 'edit')
                for object_id in object_ids
            ):
                raise self.EditRequestError(
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

    @server_only
    def serialise(self):
        '''
        For outputting to JSON in API-mode.
        '''

        return {
            key: getattr(self, key, None)
            for key in self.get_column_keys()
        }

    def save(self):
        '''
        Validate ``Object``s before saving.
        '''

        self.is_valid()

        super(Object, self).save()

    def delete(self):
        '''
        Delete ``Note``s attached to this ``Object``.
        '''

        for note in self.notes:
            db.session.delete(note)

        super(Object, self).delete()

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
        '''
        Add hooks to apply to all object sub-classes of this.
        '''

        cls.hooks[type].append(callback)
