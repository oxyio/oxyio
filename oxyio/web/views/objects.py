# oxy.io
# File: oxyio/web/views/objects.py
# Desc: list & add objects

from flask import abort, request, g
from jinja2 import TemplateNotFound
from sqlalchemy.orm import joinedload

from oxyio.data import get_object_class_or_404, get_objects, get_object

from oxyio.web.route import html_api_route
from oxyio.web.request import in_request_args, get_request_data
from oxyio.web.response import render_or_jsonify, redirect_or_jsonify
from oxyio.web.user import (
    get_own_objects,
    login_required, get_current_user,
    has_own_objects_permission, has_any_objects_permission,
    has_global_objects_permission
)


def _filter_field(objects, obj, field, value):
    # Multiple values, do an IN query
    if isinstance(value, list):
        objects = objects.filter(getattr(obj, field).in_(value))

    # Single value, simple filter
    else:
        objects = objects.filter(getattr(obj, field) == value)

    return objects


def _contains_field(objects, obj, field, value):
    return objects.filter(getattr(obj, field).contains(value))


def _do_list_objects(module_name, objects_type, get_objects_func, is_all=False):
    g.module = module_name
    g.object = objects_type

    object_class = get_object_class_or_404(module_name, objects_type)
    objects = get_objects_func(module_name, objects_type)

    # Join-load any relations
    objects = objects.options(*[
        joinedload(field)
        for field, _, _ in object_class.LIST_RELATIONS
    ])

    # Join-load any multi relations
    objects = objects.options(*[
        joinedload(field)
        for field, _, _ in object_class.LIST_MRELATIONS
    ])

    # Join-load any list fields which ask for it
    for field, options in object_class.LIST_FIELDS:
        if options.get('join'):
            objects = objects.options(joinedload(field))

    # Apply any filters
    filtered = False

    # Name filter
    if in_request_args('name'):
        filtered = True
        objects = objects.filter(
            object_class.name.like('%{0}%'.format(request.args['name']))
        )

    # Field filters
    for field, _ in object_class.FILTER_FIELDS:
        if in_request_args(field):
            filtered = True
            objects = _filter_field(
                objects, object_class, field,
                request.args[field],
            )

    # Relation filters
    for field, (module_name, objects_type), options in object_class.FILTER_RELATIONS:
        if in_request_args(field):
            filtered = True
            objects = _filter_field(
                objects, object_class, field,
                get_object(module_name, objects_type, request.args[field]),
            )

    # Multi relation filters
    for field, (module_name, objects_type), options in object_class.FILTER_MRELATIONS:
        if in_request_args(field):
            filtered = True
            objects = _contains_field(
                objects, object_class, field,
                get_object(module_name, objects_type, request.args[field]),
            )

    # Fetch the objects
    objects = list(objects)

    # Build filter form
    filter_form = object_class().build_filter_form()

    return render_or_jsonify('objects/list.html', {
        'object_class': object_class,
        'filter_form': filter_form,
        'filtered': filtered,
        'action': 'all' if is_all else 'own',
    },
        module_name=module_name,
        objects_type=objects_type,
        objects=objects,
    )


def list_objects(module_name, objects_type):
    if not has_global_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    return _do_list_objects(
        module_name, objects_type,
        get_objects_func=get_objects,
    )


def list_own_objects(module_name, objects_type):
    if not has_own_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    return _do_list_objects(
        module_name, objects_type,
        get_objects_func=get_own_objects,
    )


def list_all_objects(module_name, objects_type):
    if not has_any_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    return _do_list_objects(
        module_name, objects_type,
        get_objects_func=get_objects,
        is_all=True,
    )


def view_add_objects(module_name, objects_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, objects_type, 'add'):
        return abort(403)

    g.module = module_name
    g.object = objects_type

    # Get object class
    object_class = get_object_class_or_404(module_name, objects_type)

    # Build it's form
    add_form = object_class().build_form()

    template_data = {
        'add_form': add_form,
    }

    data = {
        'objects_type': objects_type,
        'object_class': object_class,
        'module_name': module_name,
    }

    # Load view template file from module, default to standard
    try:
        return render_or_jsonify(
            '{0}/add.html'.format(objects_type), template_data, **data
        )

    except TemplateNotFound:
        return render_or_jsonify('objects/add.html', template_data, **data)


def add_objects(module_name, object_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, object_type, 'Add'):
        return abort(403)

    g.module = module_name
    g.object = object_type

    # Get object class
    obj = get_object_class_or_404(module_name, object_type)

    # Initalize a the object
    new_object = obj()

    # Get the request data
    request_data = get_request_data()

    try:
        # Apply request data to the empty object
        new_object.edit(request_data)

        # If this object can be owned, set the user_id to the current user
        if obj.OWNABLE:
            new_object.user_id = get_current_user().id

        # Validate & save it
        new_object.save()

    except (new_object.EditRequestError, new_object.ValidationError) as e:
        return redirect_or_jsonify(error=e.message)

    # Post add & hooks
    new_object.post_add()
    for f in new_object.hooks['post_add']:
        f()

    # Redirect to it
    return redirect_or_jsonify(
        new_object.view_url,
        success='{0} Added'.format(obj.TITLE),
    )


def create_objects_views(app, api_app, cls):
    args = (cls.MODULE, cls.OBJECT)

    # Create list views
    if cls.OWNABLE:
        # List own objects
        html_api_route(
            '/{0}s'.format(cls.OBJECT),
            methods=['GET'],
            endpoint='list_own_{0}s'.format(cls.OBJECT),
            app=app, api_app=api_app,
        )(login_required(lambda: list_own_objects(*args)))

        # Create list all view
        html_api_route(
            '/{0}s/all'.format(cls.OBJECT),
            methods=['GET'],
            endpoint='list_all_{0}s'.format(cls.OBJECT),
            app=app, api_app=api_app,
        )(login_required(lambda: list_all_objects(*args)))

    else:
        # List "global" objects
        html_api_route(
            '/{0}s'.format(cls.OBJECT),
            methods=['GET'],
            endpoint='list_{0}s'.format(cls.OBJECT),
            app=app, api_app=api_app,
        )(login_required(lambda: list_objects(*args)))

    if cls.ADDABLE:
        # Create view add view
        app.route(
            '/{0}s/add'.format(cls.OBJECT),
            methods=['GET'],
            endpoint='view_add_{0}s'.format(cls.OBJECT),
        )(login_required(lambda: view_add_objects(*args)))

        # Create POST add view
        html_api_route(
            '/{0}s/add'.format(cls.OBJECT),
            methods=['POST'],
            endpoint='add_{0}s'.format(cls.OBJECT),
            app=app, api_app=api_app,
        )(login_required(lambda: add_objects(*args)))
