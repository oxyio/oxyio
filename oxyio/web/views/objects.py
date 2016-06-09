# oxy.io
# File: oxyio/views/objects.py
# Desc: list & add objects

from flask import abort, request, g
from jinja2 import TemplateNotFound
from sqlalchemy.orm import joinedload

from oxyio.data import get_object_class_or_404, get_objects
from oxyio.models.object import iter_relations
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
    if ',' in request.args[field]:
        values = request.args[field].split(',')
        objects = objects.filter(getattr(obj, field).in_(values))

    # Single value, simple filter
    else:
        objects = objects.filter_by(**{field: request.args[field]})

    return objects


def _do_list_objects(module_name, objects_type, obj, objects, is_all=False):
    # Join-load any relations
    objects = objects.options(*[
        joinedload(field)
        for field, _, _ in obj.LIST_RELATIONS
    ])

    # Join-load any multi relations
    objects = objects.options(*[
        joinedload(field)
        for field, _, _ in obj.LIST_MRELATIONS
    ])

    # Join-load any list fields which ask for it
    for (field, options) in obj.LIST_FIELDS:
        if options.get('join'):
            objects = objects.options(joinedload(field))

    # Apply any filters
    filtered = False

    for (field, _) in obj.FILTER_FIELDS:
        if in_request_args(field):
            filtered = True
            objects = _filter_field(objects, obj, field, request.args[field])

    # Name filter
    if 'name' in request.args and len(request.args['name']) > 0:
        filtered = True
        objects = objects.filter(
            obj.name.like('%{0}%'.format(request.args['name']))
        )

    # Fetch the objects
    objects = list(objects)

    # Build filter form
    filter_form = obj().build_filter_form()

    return render_or_jsonify('object/list.html', {
        'object_name': obj.TITLE,
        'objects_name': obj.TITLES,
        'list_fields': obj.LIST_FIELDS,
        'list_relations': list(iter_relations(obj.LIST_RELATIONS)),
        'list_mrelations': list(iter_relations(obj.LIST_MRELATIONS)),
        'filter_form': filter_form,
        'action': 'all' if is_all else 'own',
        'filtered': filtered
    },
        module_name=module_name,
        objects_type=objects_type,
        objects=objects
    )


def list_objects(module_name, objects_type):
    if not has_own_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    g.module = module_name
    g.object = objects_type

    obj = get_object_class_or_404(module_name, objects_type)
    objects = get_own_objects(module_name, objects_type)

    return _do_list_objects(module_name, objects_type, obj, objects)


def list_all_objects(module_name, objects_type):
    if not has_any_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    g.module = module_name
    g.object = objects_type

    obj = get_object_class_or_404(module_name, objects_type)

    # Get objects
    objects = get_objects(module_name, objects_type)

    return _do_list_objects(module_name, objects_type, obj, objects, is_all=True)


def view_add_objects(module_name, objects_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, objects_type, 'Add'):
        return abort(403)

    g.module = module_name
    g.object = objects_type

    # Get object class
    obj = get_object_class_or_404(module_name, objects_type)

    # Build it's form
    add_form = obj().build_form()

    data = {
        'add_form': add_form,
        'objects_type': objects_type,
        'object_name': obj.TITLE,
        'objects_name': obj.TITLES,
        'module_name': module_name
    }

    # Load view template file from module, default to standard
    try:
        return render_or_jsonify('{0}/add.html'.format(objects_type), **data)
    except TemplateNotFound:
        return render_or_jsonify('object/add.html', **data)


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

        # Set the user_id to the current user
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
        success='{0} Added'.format(obj.TITLE)
    )


def create_objects_views(app, api_app, cls):
    args = (cls.MODULE, cls.OBJECT)

    # Create list view
    html_api_route(
        '/{0}s'.format(cls.OBJECT),
        methods=['GET'],
        endpoint='list_{0}s'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda: list_objects(*args)))

    # Create list all view
    html_api_route(
        '/{0}s/all'.format(cls.OBJECT),
        methods=['GET'],
        endpoint='list_all_{0}s'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda: list_all_objects(*args)))

    # Create GET add view
    html_api_route(
        '/{0}s/add'.format(cls.OBJECT),
        methods=['GET'],
        endpoint='view_add_{0}s'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda: view_add_objects(*args)))

    # Create POST add view
    html_api_route(
        '/{0}s/add'.format(cls.OBJECT),
        methods=['POST'],
        endpoint='add_{0}s'.format(cls.OBJECT),
        app=app, api_app=api_app
    )(login_required(lambda: add_objects(*args)))
