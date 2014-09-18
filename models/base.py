# Oxypanel
# File: models/base.py
# Desc: BaseObject and BaseItem
#       objects are owned by users and/or groups
#       items are owned by objects

from flask import request
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declared_attr

from app import db
from util import log
from util.data import get_objects, get_object_class, get_object
from util.user import get_current_user


# Map string types -> python types
STRING_TO_PYTHON = {
    'int': int,
    'enum': set,
    'string': str
}

# Map column types -> string_type, python_type, col args
def _column_to_python(column):
    # Integers
    if isinstance(column, db.Integer):
        return ('int', int, None)
    # Enums (which almost match db.String)
    elif isinstance(column, db.Enum):
        return ('enum', set, column.enums)
    # Strings
    elif isinstance(column, db.String):
        return ('string', str, column.length)
    # Oh shit!
    else:
        log.warning('unknown column type: {0}'.format(type(column)))


class BaseConfig:
    NAME = ''
    NAMES = ''

    LIST_FIELDS = EDIT_FIELDS = []
    LIST_RELATIONS = EDIT_RELATIONS = []

    ROUTES = []

class BaseObject:
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

    # For outputting to JSON in API-mode
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

    # Turn device config fields into form tuples
    def _config_to_form(self, fields):
        form = []
        for (field, options) in fields:
            override = options.get('override')
            if override:
                arg = getattr(self, override[1])()
                form.append((field, override[0], arg, override[2]))
            else:
                col = self.__table__.columns.get(field)
                string_type, _, arg = _column_to_python(col.type)
                form.append((field, string_type, arg, options))

        return form

    # Builds the list the form function in `forms.html` wants
    def build_form(self):
        # Normal edit fields + name
        form = self._config_to_form([('name', {})] + self.Config.EDIT_FIELDS)

        # Related objects
        user = get_current_user()
        for (module_name, objects_type, options) in self.Config.EDIT_RELATIONS:
            obj = get_object_class(module_name, objects_type)
            form.append((
                '{0}_id'.format(objects_type),
                'relation',
                get_objects(module_name, objects_type, or_(
                    obj.user_id==user.id,
                    obj.user_group_id==(-1 if user.user_group_id is None else user.user_group_id)
                )),
                options
            ))

        return form

    def build_filter_form(self):
        # List fields
        form = self._config_to_form(self.Config.LIST_FIELDS)
        return form

    # Check and apply self.Config.EDIT_FIELDS to self
    # returns list of errors, or empty list for success
    def check_apply_edit_fields(self):
        # Check name
        name = request.form.get('name')
        if not name or len(name) <= 0:
            return False, 'Invalid name'

        setattr(self, 'name', name)

        for (field, options) in self.Config.EDIT_FIELDS:
            data = request.form.get(field)
            if data is not None:
                # Verify the field is valid
                override = options.get('override')
                if override:
                    python_type = STRING_TO_PYTHON[override[0]]
                    arg = getattr(self, override[1])()
                else:
                    col = self.__table__.columns.get(field)
                    _, python_type, arg = _column_to_python(col.type)

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
        for (module_name, object_type, _) in self.Config.EDIT_RELATIONS:
            field_name = '{0}_id'.format(object_type)
            data = request.form.get(field_name)

            try:
                data = int(data)
                if data == 0: data = None
            except ValueError:
                data = None
                return False, 'Invalid data, not ID for: {0}'.format(object_type)

            # Try to find the object
            if data is not None:
                obj = get_object(module_name, object_type, data)
                if not obj:
                    return False, 'Invalid related object ({0} {1})'.format(module_name, object_type)

            # Set the object
            setattr(self, field_name, data)

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

    # Add the hooks
    @classmethod
    def add_hook(self, type, callback):
        self.hooks[type].append(callback)


class BaseItem:
    id = db.Column(db.Integer, primary_key=True)
