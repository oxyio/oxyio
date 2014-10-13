# Oxypanel
# File: views/admin/permissions.py
# Desc: view & edit system permissions

from flask import g

from app import app, object_map
from util.response import render_or_jsonify
from util.user import permissions_required
from models.user import UserGroup


@app.route('/admin/permissions', methods=['GET'])
@permissions_required('Admin', 'AdminPermissions')
def admin_permissions():
    g.module = 'admin'

    # Core permissions
    permissions = {
        'core': [
            'Admin',
            'AdminSettings',
            'AdminUsers',
            'AdminPermissions',
            'AdminLogs',
            'AdminDebug'
        ],
        'objects': {}
    }

    # Object permissions
    for module_name, objects in object_map.iteritems():
        module_title = module_name.title()
        for object_name, object_class in objects.iteritems():
            object_title = object_name.title()

            permissions['objects'][object_name] = [
                'ViewOwn{0}{1}'.format(module_title, object_title),
                'EditOwn{0}{1}'.format(module_title, object_title),
                'ViewAny{0}{1}'.format(module_title, object_title),
                'EditAny{0}{1}'.format(module_title, object_title),
                'Add{0}{1}'.format(module_title, object_title),
                'Delete{0}{1}'.format(module_title, object_title),
                'Owner{0}{1}'.format(module_title, object_title)
            ]

    groups = UserGroup.query.all()
    return render_or_jsonify('admin/permissions.html',
        action='permissions',
        permissions=permissions,
        groups=groups
    )
