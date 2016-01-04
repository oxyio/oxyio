# oxy.io
# File: oxyio/views/objects.py
# Desc: list & add objects

from flask import abort, request
from jinja2 import TemplateNotFound
from sqlalchemy.orm import joinedload

from oxyio.app import web_app
from oxyio.models.base import iter_relations
from oxyio.util.data import get_object_class_or_404, get_objects
from oxyio.web.util.route import html_api_route
from oxyio.web.util.request import in_request_args
from oxyio.web.util.response import render_or_jsonify, redirect_or_jsonify
from oxyio.web.util.user import (
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
    for (field, _) in obj.FILTER_FIELDS:
        if in_request_args(field):
            objects = _filter_field(objects, obj, field, request.args[field])

    # Name filter
    if 'name' in request.args and len(request.args['name']) > 0:
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
        'action': 'all' if is_all else 'own'
    },
        module_name=module_name,
        objects_type=objects_type,
        objects=objects
    )


@html_api_route(
    '/<string:module_name>/<regex("[a-zA-Z_]+"):objects_type>s/all',
    methods=['GET']
)
@login_required
def list_all_objects(module_name, objects_type):
    if not has_any_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    obj = get_object_class_or_404(module_name, objects_type)

    # Get objects
    objects = get_objects(module_name, objects_type)

    return _do_list_objects(module_name, objects_type, obj, objects, is_all=True)


@html_api_route(
    '/<string:module_name>/<regex("[a-zA-Z_]+"):objects_type>s',
    methods=['GET']
)
@login_required
def list_objects(module_name, objects_type):
    if not has_own_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    obj = get_object_class_or_404(module_name, objects_type)
    objects = get_own_objects(module_name, objects_type)

    return _do_list_objects(module_name, objects_type, obj, objects)


@web_app.route(
    '/<string:module_name>/<regex("[a-zA-Z_]+"):objects_type>s/add',
    methods=['GET']
)
@login_required
def view_add_objects(module_name, objects_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, objects_type, 'Add'):
        return abort(403)

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


@html_api_route(
    '/<string:module_name>/<regex("[a-zA-Z_]+"):object_type>s/add',
    methods=['POST']
)
@login_required
def add_objects(module_name, object_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, object_type, 'Add'):
        return abort(403)

    # Get object class
    obj = get_object_class_or_404(module_name, object_type)

    # Initalize a the object
    new_object = obj()

    # Apply EDIT_FIELDS & basic field check
    try:
        new_object.check_apply_edit_fields()
        new_object.is_valid(new=True)

    except new_object.ValidationError as e:
        return redirect_or_jsonify(error=e.message)

    # Set the user_id to current user
    new_object.user_id = get_current_user().id

    # Save it!
    new_object.save()

    # Post add & hooks
    new_object.post_add()
    for f in new_object.hooks['post_add']:
        f()

    # Redirect to it
    return redirect_or_jsonify(
        new_object.view_url,
        success='{0} Added'.format(obj.TITLE)
    )
