# Oxypanel
# File: views/object.py
# Desc: Flask routes for internal object calls

from flask import abort, request, url_for
from jinja2 import TemplateNotFound

from app import app
from models.user import User, UserGroup
from util.user import has_object_permission, login_required, has_global_objects_permission
from util.objects import get_object_or_404
from util.web.response import redirect_or_jsonify, render_or_jsonify


@app.route('/<string:module_name>/<string:object_type>/<int:object_id>', methods=['GET'])
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


@app.route('/<string:module_name>/<string:object_type>/<int:object_id>/edit', methods=['GET'])
@login_required
def view_edit_object(module_name, object_type, object_id):
    # Check permission (can't use decorator as need object_type)
    if not has_object_permission(module_name, object_type, object_id, 'edit'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Apply it's pre_view_edit function
    obj.pre_view_edit()

    # Build it's form (respects Config.EDIT_FIELDS)
    edit_form = obj.build_form()

    data = {
        'module_name': module_name,
        'object_type': object_type,
        'object': obj,
        'edit_form': edit_form,
        'action': 'edit'
    }

    # Load view template file from module, default to standard
    try:
        return render_or_jsonify('{0}/edit.html'.format(object_type), **data)
    except TemplateNotFound:
        return render_or_jsonify('object/edit.html', **data)

@app.route('/<string:module_name>/<string:object_type>/<int:object_id>',
    methods=['POST'])
@login_required
def edit_object(module_name, object_type, object_id):
    # Check permission
    if not has_object_permission(module_name, object_type, object_id, 'edit'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)
    # Apply EDIT_FIELDS & basic field check & is_valid check
    status, error = obj.check_apply_edit_fields()
    status, error = (status, error) if status is not True else obj.is_valid()
    if not status:
        return redirect_or_jsonify(url='{0}/edit'.format(request.url), error=error)

    # Save
    obj.save()

    # Post edit & hooks
    obj.post_edit()
    for f in obj.hooks['post_edit']: f()

    return redirect_or_jsonify(
        url=url_for('view_edit_object',
            module_name=module_name,
            object_type=object_type,
            object_id=object_id
        ),
        success='{0} updated'.format(obj.Config.NAME)
    )


@app.route('/<string:module_name>/<string:object_type>/<int:object_id>/delete', methods=['POST'])
@login_required
def delete_object(module_name, object_type, object_id):
    # Check permission
    if not has_global_objects_permission(module_name, object_type, 'delete'):
        return abort(403)

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Check pre_delete function
    status, error = obj.pre_delete()
    if not status:
        return redirect_or_jsonify(error=error)

    # Delete!
    obj.delete()

    # Post delete & hooks
    obj.post_delete()
    for f in obj.hooks['post_delete']: f()


@app.route('/<string:module_name>/<string:object_type>/<int:object_id>/owner', methods=['GET'])
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

@app.route('/<string:module_name>/<string:object_type>/<int:object_id>/owner', methods=['POST'])
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
    return redirect_or_jsonify(success='{0} owner changed'.format(object_type.title()))


@app.route('/<string:module_name>/<string:object_type>/<int:object_id>/<string:func_name>', methods=['GET', 'POST'])
@login_required
def custom_function_object(module_name, object_type, object_id, func_name):
    # Get object from module
    obj = get_object_or_404(module_name, object_type, object_id)

    # Try to find the route
    func_name = '/{0}'.format(func_name)
    route_i = [i for i, v in enumerate(obj.Config.ROUTES) if v[0] == func_name]
    if not route_i:
        return abort(404)

    _, methods, func, permission = obj.Config.ROUTES[route_i[0]]

    # Check permission
    if not has_object_permission(module_name, object_type, object_id, permission):
        return abort(403)

    # Wrong method? cya
    if request.method not in methods:
        return abort(405)

    return func(obj)
