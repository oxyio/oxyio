# oxy.io
# File: oxyio/views/admin/permissions.py
# Desc: view & edit system permissions

from flask import g, request, url_for, abort

from oxyio.app import web_app, db, object_map
from oxyio.models.user import UserGroup, Permission
from oxyio.web.response import render_or_jsonify, redirect_or_jsonify
from oxyio.web.user import permissions_required


def _get_group_or_404(group_id):
    group = UserGroup.query.get(group_id)
    if not group:
        abort(404)

    return group


@web_app.route('/admin/permissions', methods=['GET'])
@permissions_required('AdminPermissions')
def admin_permissions():
    g.module = 'admin'

    permissions = {
        # Core admin permissions
        'Admin': [
            ('AdminSettings', 'Edit settings'),
            ('AdminUsers', 'Add/modify users'),
            ('AdminPermissions', 'Edit permissions & groups'),
            ('AdminTasks', 'View current tasks'),
            ('AdminLogs', 'View logs'),
            ('AdminDebug', 'View debug'),
        ],
    }

    # Object permissions
    for module_name, objects in object_map.iteritems():
        module_title = module_name.title()

        # Ensure permissions list for this module
        permissions.setdefault(module_title, [])

        for object_name, object_class in objects.iteritems():
            object_title = object_name.title()

            object_permissions = [
                (
                    '{0}{1}Add'.format(module_title, object_title),
                    'Add {0} {1}'.format(module_title, object_class.TITLES)
                ),
                (
                    '{0}{1}Delete'.format(module_title, object_title),
                    'Delete {0} {1}'.format(module_title, object_class.TITLES),
                )
            ]

            if object_class.OWNABLE:
                object_permissions.extend([
                    (
                        '{0}{1}Owner'.format(module_title, object_title),
                        'Change {0} {1} owner'.format(module_title, object_class.TITLES)
                    ),
                    (
                        '{0}{1}ViewOwn'.format(module_title, object_title),
                        'View own {0} {1}'.format(module_title, object_class.TITLES)
                    ),
                    (
                        '{0}{1}EditOwn'.format(module_title, object_title),
                        'Edit own {0} {1}'.format(module_title, object_class.TITLES)
                    ),
                    (
                        '{0}{1}ViewAny'.format(module_title, object_title),
                        'View any {0} {1}'.format(module_title, object_class.TITLES)
                    ),
                    (
                        '{0}{1}EditAny'.format(module_title, object_title),
                        'Edit any {0} {1}'.format(module_title, object_class.TITLES)
                    ),
                ])

            else:
                object_permissions.extend([
                    (
                        '{0}{1}View'.format(module_title, object_title),
                        'View {0} {1}'.format(module_title, object_class.TITLES)
                    ),
                    (
                        '{0}{1}Edit'.format(module_title, object_title),
                        'Edit {0} {1}'.format(module_title, object_class.TITLES)
                    )
                ])

            permissions[module_title].extend(object_permissions)

    groups = UserGroup.query.all()
    all_permissions = Permission.query.all()

    current_permissions = {
        group.id: []
        for group in groups
    }
    for permission in all_permissions:
        current_permissions[permission.user_group_id].append(permission.name.lower())

    return render_or_jsonify(
        'admin/permissions.html',
        action='permissions',
        groups=groups,
        permissions=permissions,
        current_permissions=current_permissions,
    )


@web_app.route('/admin/permissions', methods=['POST'])
@permissions_required('AdminPermissions')
def admin_edit_permissions():
    g.module = 'admin'

    # Delete all current permissions
    Permission.query.delete()

    # Create all new ones
    for key, value in request.form.iteritems():
        if key == 'csrf_token' or not key.startswith('group-'):
            continue

        _, group_id, permission = key.split('-')
        permission = Permission(permission, group_id)
        db.session.add(permission)

    # Commit all the changes!
    db.session.commit()

    return redirect_or_jsonify(success='Permissions updated')


@web_app.route('/admin/groups', methods=['POST'])
@permissions_required('AdminPermissions')
def admin_add_group():
    name = request.form['name']
    if len(name) == 0:
        return redirect_or_jsonify(url_for('admin_users'), error='Invalid name')

    group = UserGroup(name)
    db.session.add(group)
    db.session.commit()

    return redirect_or_jsonify(
        url_for('admin_permissions'),
        success='Group added',
    )


@web_app.route('/admin/groups/<int:group_id>/edit', methods=['GET'])
@permissions_required('AdminPermissions')
def admin_view_edit_group(group_id):
    g.module = 'admin'
    group = _get_group_or_404(group_id)

    return render_or_jsonify(
        'admin/group.html',
        action='permissions',
        group=group,
    )


@web_app.route('/admin/groups/<int:group_id>/edit', methods=['POST'])
@permissions_required('AdminPermissions')
def admin_edit_group(group_id):
    name = request.form['name']
    if len(name) == 0:
        return redirect_or_jsonify(error='Invalid name')

    group = _get_group_or_404(group_id)
    group.name = name

    db.session.add(group)
    db.session.commit()

    return redirect_or_jsonify(success='Group updated')


@web_app.route('/admin/groups/<int:group_id>/delete', methods=['POST'])
@permissions_required('AdminPermissions')
def admin_delete_group(group_id):
    group = UserGroup.query.get(group_id)
    if not group:
        abort(404)

    db.session.delete(group)
    db.session.commit()

    return redirect_or_jsonify(
        url_for('admin_permissions'),
        success='Group deleted',
    )
