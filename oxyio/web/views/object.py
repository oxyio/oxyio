# oxy.io
# File: oxyio/views/object.py
# Desc: Flask routes for internal object calls

from flask import abort, request
from jinja2 import TemplateNotFound

from oxyio.app import web_app
from oxyio.models.user import User, UserGroup
from oxyio.util.data import get_object_or_404
from oxyio.web.util.route import html_api_route
from oxyio.web.util.response import redirect_or_jsonify, render_or_jsonify
from oxyio.web.util.user import (
    has_object_permission, login_required, has_global_objects_permission
)


@html_api_route(
    '/<string:module_name>/<string:object_type>/<int:object_id>',
    methods=['GET']
)
@login_required
def view_object(module_name, object_type, object_id):
    # Check permission (can't use decorator as need object_type)
    if not has_object_permission(module_name, object_type, object_id, 'view'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Apply it's pre_view function
    obj.pre_view()

    # Load view template file from module
    return render_or_jsonify('{0}/view.html'.format(object_type),
        module_name=module_name,
        object_type=object_type,
        object=obj,
        action='view'
    )


@web_app.route(
    '/<string:module_name>/<string:object_type>/<int:object_id>/edit',
    methods=['GET']
)
@login_required
def view_edit_object(module_name, object_type, object_id):
    # Check permission (can't use decorator as need object_type)
    if not has_object_permission(module_name, object_type, object_id, 'edit'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Apply it's pre_view_edit function
    obj.pre_view_edit()

    # Build it's form (respects.EDIT_FIELDS)
    edit_form = obj.build_form()

    data = {
        'module_name': module_name,
        'object_type': object_type,
        'object': obj,
        'edit_form': edit_form,
        'action': 'edit'
    }

    # Try loading object specific template
    try:
        return render_or_jsonify('{0}/edit.html'.format(object_type), **data)

    # Default to standard template
    except TemplateNotFound:
        return render_or_jsonify('object/edit.html', **data)


@html_api_route(
    '/<string:module_name>/<string:object_type>/<int:object_id>/edit',
    methods=['POST']
)
@login_required
def edit_object(module_name, object_type, object_id):
    # Check permission
    if not has_object_permission(module_name, object_type, object_id, 'edit'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Apply EDIT_FIELDS & basic field check & is_valid check
    try:
        obj.check_apply_edit_fields()
        obj.is_valid()

    except obj.ValidationError as e:
        return redirect_or_jsonify(error=e.message)

    # Save
    obj.save()

    # Post edit & hooks
    obj.post_edit()
    for hook in obj.hooks['post_edit']:
        hook()

    return redirect_or_jsonify(
        obj.view_url,
        success='{0} updated'.format(obj.TITLE)
    )


@html_api_route(
    '/<string:module_name>/<string:object_type>/<int:object_id>/delete',
    methods=['POST']
)
@login_required
def delete_object(module_name, object_type, object_id):
    # Check permission
    if not has_global_objects_permission(module_name, object_type, 'delete'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Check pre_delete function
    try:
        obj.pre_delete()
    except obj.DeletionError as e:
        return redirect_or_jsonify(error=e.message)

    # Delete!
    obj.delete()

    # Post delete & hooks
    obj.post_delete()
    for hook in obj.hooks['post_delete']:
        hook()


@web_app.route(
    '/<string:module_name>/<string:object_type>/<int:object_id>/owner',
    methods=['GET']
)
@login_required
def view_owner_object(module_name, object_type, object_id):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, object_type, 'owner'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Get all users & user_groups
    users = User.query.all()
    groups = UserGroup.query.all()

    # Load view template file from module
    return render_or_jsonify('object/owner.html'.format(object_type),
        module_name=module_name,
        object_type=object_type,
        object=obj,
        users=users,
        groups=groups,
        action='owner'
    )


@html_api_route(
    '/<string:module_name>/<string:object_type>/<int:object_id>/owner',
    methods=['POST']
)
@login_required
def owner_object(module_name, object_type, object_id):
    # Check permission
    if not has_global_objects_permission(module_name, object_type, 'owner'):
        return abort(403)

    # Check user and/or group exist
    user_id, group_id = request.form.get('user_id'), request.form.get('group_id')
    try:
        user_id, group_id = int(user_id), int(group_id)
    except ValueError:
        return redirect_or_jsonify(error='Invalid user or group')

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Set user_id & user_group_id
    obj.user_id = user_id if user_id > 0 else None
    obj.user_group_id = group_id if group_id > 0 else None

    # Save & redirect
    obj.save()
    return redirect_or_jsonify(success='{0} owner changed'.format(obj.TITLE))


@html_api_route(
    '/<string:module_name>/<string:object_type>/<int:object_id>/<string:func_name>',
    methods=['GET', 'POST']
)
@login_required
def custom_function_object(module_name, object_type, object_id, func_name):
    # Get object from module
    obj = get_object_or_404(module_name, object_type, object_id)

    # Try to find the route
    func_name = '/{0}'.format(func_name)
    route_i = [i for i, v in enumerate(obj.ROUTES) if v[0] == func_name]
    if not route_i:
        return abort(404)

    _, methods, func, permission = obj.ROUTES[route_i[0]]

    # Check permission
    if not has_object_permission(module_name, object_type, object_id, permission):
        return abort(403)

    # Wrong method? cya
    if request.method not in methods:
        return abort(405)

    return func(obj)
