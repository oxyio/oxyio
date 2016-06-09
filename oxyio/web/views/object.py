# oxy.io
# File: oxyio/views/object.py
# Desc: Flask routes for internal object calls

from flask import abort, request, g
from jinja2 import TemplateNotFound

from oxyio.models.user import User, UserGroup
from oxyio.data import get_object_or_404
from oxyio.web.route import html_api_route
from oxyio.web.request import get_request_data
from oxyio.web.response import redirect_or_jsonify, render_or_jsonify
from oxyio.web.user import (
    has_object_permission, login_required, has_global_objects_permission
)


def view_object(object_id, module_name, object_type):
    # Check permission (can't use decorator as need object_type)
    if not has_object_permission(module_name, object_type, object_id, 'view'):
        return abort(403)

    g.module = module_name
    g.object = object_type

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


def view_edit_object(object_id, module_name, object_type):
    # Check permission (can't use decorator as need object_type)
    if not has_object_permission(module_name, object_type, object_id, 'edit'):
        return abort(403)

    g.module = module_name
    g.object = object_type

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


def edit_object(object_id, module_name, object_type):
    # Check permission
    if not has_object_permission(module_name, object_type, object_id, 'edit'):
        return abort(403)

    g.module = module_name
    g.object = object_type

    # Get object
    obj = get_object_or_404(module_name, object_type, object_id)

    # Get the request data
    request_data = get_request_data()

    try:
        # Update the object with our request data
        obj.edit(request_data)

        # Validate & save the object
        obj.save()

    except (obj.EditRequestError, obj.ValidationError) as e:
        return redirect_or_jsonify(error=e.message)

    # Post edit & hooks
    obj.post_edit()
    for hook in obj.hooks['post_edit']:
        hook()

    return redirect_or_jsonify(
        obj.view_url,
        success='{0} updated'.format(obj.TITLE)
    )


def delete_object(object_id, module_name, object_type):
    # Check permission
    if not has_global_objects_permission(module_name, object_type, 'delete'):
        return abort(403)

    g.module = module_name
    g.object = object_type

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


def view_owner_object(object_id, module_name, object_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, object_type, 'owner'):
        return abort(403)

    g.module = module_name
    g.object = object_type

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


def owner_object(object_id, module_name, object_type):
    # Check permission
    if not has_global_objects_permission(module_name, object_type, 'owner'):
        return abort(403)

    g.module = module_name
    g.object = object_type

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


def custom_function_object(object_id, view_func, permission, module_name, object_type):
    # Get object from module
    obj = get_object_or_404(module_name, object_type, object_id)

    # Check permission
    if not has_object_permission(module_name, object_type, object_id, permission):
        return abort(403)

    return view_func(obj)


def create_object_views(app, api_app, cls):
    args = (cls.MODULE, cls.OBJECT)

    # Create view view
    html_api_route(
        '/{0}/<int:object_id>'.format(cls.OBJECT),
        methods=['GET'],
        endpoint='view_{0}'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda object_id: view_object(object_id, *args)))

    # Create GET edit view
    html_api_route(
        '/{0}/<int:object_id>/edit'.format(cls.OBJECT),
        methods=['GET'],
        endpoint='view_edit_{0}'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda object_id: view_edit_object(object_id, *args)))

    # Create POST edit view
    html_api_route(
        '/{0}/<int:object_id>/edit'.format(cls.OBJECT),
        methods=['POST'],
        endpoint='edit_{0}'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda object_id: edit_object(object_id, *args)))

    # Create GET owner view
    html_api_route(
        '/{0}/<int:object_id>/owner'.format(cls.OBJECT),
        methods=['GET'],
        endpoint='view_owner_{0}'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda object_id: view_owner_object(object_id, *args)))

    # Create POST owner view
    html_api_route(
        '/{0}/<int:object_id>/owner'.format(cls.OBJECT),
        methods=['POST'],
        endpoint='owner_{0}'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda object_id: owner_object(object_id, *args)))

    # Create delete view
    html_api_route(
        '/{0}/<int:object_id>/delete'.format(cls.OBJECT),
        methods=['POST'],
        endpoint='delete_{0}'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda object_id: delete_object(object_id, *args)))

    # Add custom object routes
    for name, methods, view_func, permission in cls.ROUTES:
        html_api_route(
            '/{0}/<int:object_id>/{1}'.format(cls.OBJECT, name),
            methods=methods,
            endpoint='{0}_{1}'.format(cls.OBJECT, name),
            app=app, api_app=api_app
        )(login_required(lambda object_id: custom_function_object(
            object_id, view_func, permission, *args
        )))
