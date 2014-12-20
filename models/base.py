# Oxypanel
# File: models/base.py
# Desc: BaseObject and BaseItem
#       objects are owned by users and/or groups
#       items are owned by objects

from flask import request
from sqlalchemy.ext.declarative import declared_attr

from app import db
from util import log
from util.data import get_object_class
from util.web.user import (
    get_own_objects, get_object,
    has_own_objects_permission, has_object_permission
)


# Maps string types -> python types
STRING_TO_PYTHON = {
    'int': int,
    'enum': set,
    'string': str
}

def _column_to_python(column):
    '''Map column types -> string_type, python_type, col args'''
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
        log.warning('unknown column type: {0}'.format(type(column)))


class BaseItem(object):
    _type = 'item'
    id = db.Column(db.Integer, primary_key=True)

class BaseObject(object):
    _type = 'object'

    ## Config section
    NAME = TITLE = TITLES = None

    LIST_FIELDS = EDIT_FIELDS = []
    LIST_RELATIONS = EDIT_RELATIONS = []
    LIST_MRELATIONS = EDIT_MRELATIONS = []

    ROUTES = []

    ## Database/struct section
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    @declared_attr
    def user(cls):
        return db.relationship('User')

    @declared_attr
    def user_group_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user_group.id', ondelete='SET NULL'))
    @declared_attr
    def user_group(cls):
        return  db.relationship('UserGroup')

    ## Base functions
    def serialize(self):
        '''For outputting to JSON in API-mode'''
        return {
            'id': self.id,
            'name': self.name
        }

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
        '''Turn device config fields into form tuples'''
        form = []
        for (field, options) in fields:
            string_type, _, arg = self._col_to_data(field, options)
            form.append((string_type, field, arg, options))

        return form

    def build_form(self):
        '''Builds an object edit/add form for macro in `function/forms.html`'''
        # Normal edit fields + name
        form = self._config_to_form([('name', {})] + self.EDIT_FIELDS)

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
        for (module_name, objects_type, options) in self.EDIT_RELATIONS:
            _do_relation('relation', module_name, objects_type, '{0}_id'.format(objects_type), options)

        # Many/Multi-related objects
        for (module_name, objects_type, objects_field, options) in self.EDIT_MRELATIONS:
            obj = get_object_class(module_name, objects_type)
            options['related_ids'] = [obj.id for obj in getattr(self, objects_field)]
            _do_relation('mrelation', module_name, objects_type, objects_field, options)

        return form

    def build_filter_form(self):
        '''Builds the objects filter/search form for macro in `function/forms.html`'''
        # Uses just list fields
        form = self._config_to_form(self.LIST_FIELDS)
        return form

    def check_apply_edit_fields(self):
        '''
        Check and apply self.EDIT_FIELDS to self
        returns list of errors, or empty list for success
        '''
        # Check name
        name = request.form.get('name')
        if not name or len(name) <= 0:
            return False, 'Invalid name'

        setattr(self, 'name', name)

        for (field, options) in self.EDIT_FIELDS:
            data = request.form.get(field)
            if data is not None:
                _, python_type, arg = self._col_to_data(field, options)

                if python_type is int:
                    try:
                        data = int(data)
                    except ValueError:
                        return False, 'Invalid data for {0}'.format(field)
                if python_type is set:
                    if data not in arg:
                        return False, 'Invalid data for {0}; {1} is not in set {2}'.format(field, data, arg)
                if python_type is str:
                    length = len(data)
                    if length > arg:
                        return False, 'String to long for {0}, limit is {1}'.format(field, arg)

                # Set the value, for custom .is_valid if supplied
                setattr(self, field, data)

        # Ensure related items exist
        for (module_name, object_type, _) in self.EDIT_RELATIONS:
            field_name = '{0}_id'.format(object_type)
            object_id = request.form.get(field_name)

            try:
                object_id = int(object_id)
                if object_id == 0: object_id = None
            except ValueError:
                return False, 'Invalid object_id for: {0}'.format(object_type)

            # Skip if set None or no change
            if object_id is None or getattr(self, field_name) == object_id:
                continue

            # Check we even have edit permission on this object type
            if not has_object_permission(module_name, object_type, object_id, 'Edit'):
                return False, 'You do not have permission to set {0} => {1} #{2}'.format(field_name, object_type, object_id)

            # Set the object
            setattr(self, field_name, object_id)

        # Ensure mrelated items exist
        for (module_name, object_type, field_name, _) in self.EDIT_MRELATIONS:
            object_ids = request.form.getlist(field_name)

            try:
                object_ids = set([int(i) for i in object_ids])
            except ValueError:
                return False, 'Invalid object_ids for: {0}'.format(object_type)

            # Check edit permissions for each object
            if not all(has_object_permission(module_name, object_type, object_id, 'Edit') for object_id in object_ids):
                return False, 'You do not have permission to set {0} => {1} #s: {2}'.format(field_name, object_type, object_ids)

            # Set the objects
            new_objects = [get_object(module_name, object_type, object_id) for object_id in object_ids if object_id > 0]
            setattr(self, field_name, new_objects)

        return True, None

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # Internal hooks
    def is_valid(self, new=False):
        return True, None
    def pre_delete(self):
        return True

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

    # External hooks (implemented in object.py & objects.py)
    hooks = {
        'post_delete': [],
        'post_edit': [],
        'post_add': []
    }

    @classmethod
    def add_hook(self, type, callback):
        '''Add hooks to apply to all object sub-classes of this'''
        self.hooks[type].append(callback)
