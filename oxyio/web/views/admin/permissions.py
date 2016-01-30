# oxy.io
# File: oxyio/views/admin/permissions.py
# Desc: view & edit system permissions

from flask import g, request

from oxyio.app import web_app, db, object_map
from oxyio.models.user import UserGroup, Permission
from oxyio.web.response import render_or_jsonify, redirect_or_jsonify
from oxyio.web.user import permissions_required


@web_app.route('/admin/permissions', methods=['GET'])
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
        'modules': [],
        'objects': {}
    }

    # Object permissions
    for module_name, objects in object_map.iteritems():
        module_title = module_name.title()
        permissions['modules'].append(module_title)
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
    all_permissions = Permission.query.all()

    current_permissions = {
        group.id: []
        for group in groups
    }
    for permission in all_permissions:
        current_permissions[permission.user_group_id].append(permission.name.lower())

    return render_or_jsonify('admin/permissions.html',
        action='permissions',
        permissions=permissions,
        groups=groups,
        current_permissions=current_permissions
    )


@web_app.route('/admin/permissions', methods=['POST'])
@permissions_required('Admin', 'AdminPermissions')
def admin_edit_permissions():
    g.module = 'admin'

    # Delete all current permissions
    Permission.query.delete()

    # Create all new ones
    for key, value in request.form.iteritems():
        if key == 'csrf_token': continue
        if not key.startswith('group-'): continue

        _, group_id, permission = key.split('-')
        permission = Permission(permission, group_id)
        db.session.add(permission)

    # Commit all the changes!
    db.session.commit()

    return redirect_or_jsonify(success='Permissions updated')
