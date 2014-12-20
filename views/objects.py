# Oxypanel
# File: views/objects.py
# Desc: list & add objects

from flask import abort, request, url_for
from jinja2 import TemplateNotFound

from app import app
from util.data import get_object_class_or_404, get_objects
from util.web.response import render_or_jsonify, redirect_or_jsonify
from util.web.user import (
    get_own_objects,
    login_required, get_current_user,
    has_own_objects_permission, has_any_objects_permission,
    has_global_objects_permission
)


def _do_list_objects(module_name, objects_type, obj, objects, is_all=False):
    # Apply any filters
    for (field, _) in obj.LIST_FIELDS:
        if field in request.args and len(request.args[field]) > 0:
            objects = objects.filter(getattr(obj, field).like('%{}%'.format(request.args[field])))

    # Name filter
    if 'name' in request.args and len(request.args['name']) > 0:
        objects = objects.filter(obj.name.like('%{}%'.format(request.args['name'])))

    # Build filter form
    filter_form = obj().build_filter_form()

    return render_or_jsonify('object/list.html',
        module_name=module_name,
        objects_type=objects_type,
        object_name=obj.TITLE,
        objects_name=obj.TITLES,
        list_fields=obj.LIST_FIELDS,
        list_relations=obj.LIST_RELATIONS,
        list_mrelations=obj.LIST_MRELATIONS,
        objects=objects,
        filter_form=filter_form,
        action=('own' if not is_all else 'all')
    )

@app.route('/<string:module_name>/<regex("[a-zA-Z_]+"):objects_type>s/all', methods=['GET'])
@login_required
def list_all_objects(module_name, objects_type):
    if not has_any_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    obj = get_object_class_or_404(module_name, objects_type)

    # Get objects
    objects = get_objects(module_name, objects_type)
    return _do_list_objects(module_name, objects_type, obj, objects, is_all=True)

@app.route('/<string:module_name>/<regex("[a-zA-Z_]+"):objects_type>s', methods=['GET'])
@login_required
def list_objects(module_name, objects_type):
    if not has_own_objects_permission(module_name, objects_type, 'view'):
        return abort(403)

    obj = get_object_class_or_404(module_name, objects_type)
    objects = get_own_objects(module_name, objects_type)
    return _do_list_objects(module_name, objects_type, obj, objects)


@app.route('/<string:module_name>/<regex("[a-zA-Z_]+"):objects_type>s/add', methods=['GET'])
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

@app.route('/<string:module_name>/<regex("[a-zA-Z_]+"):object_type>s/add', methods=['POST'])
@login_required
def add_objects(module_name, object_type):
    # Check permission (can't use decorator as need object_type)
    if not has_global_objects_permission(module_name, object_type, 'Add'):
        return abort(403)

    # Get object class
    obj = get_object_class_or_404(module_name, object_type)

    # Initalize a the object
    new_object = obj()
    # Apply EDIT_FIELDS & basic field check & is_valid check
    status, error = new_object.check_apply_edit_fields()
    status, error = (status, error) if status is not True else new_object.is_valid(new=True)
    if not status:
        return redirect_or_jsonify(error=error)

    # Set the user_id to current user
    new_object.user_id = get_current_user().id

    # Save it!
    new_object.save()

    # Post add & hooks
    new_object.post_add()
    for f in new_object.hooks['post_add']: f()

    # Redirect to it
    return redirect_or_jsonify(
        url=url_for('edit_object',
            module_name=module_name,
            object_type=object_type,
            object_id=new_object.id
        ),
        success='{0} Added'.format(obj.TITLE)
    )
