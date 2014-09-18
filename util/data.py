# Oxypanel
# File: util/app.py
# Desc: global loading of modules & their objects

from flask import abort

from app import module_map, object_map


def get_module(module_name):
    return module_map.get(module_name)

def get_module_or_404(*args, **kwargs):
    result = get_module(*args, **kwargs)
    if not result:
        return abort(404)

    return result


def get_object_class(module_name, object_type):
    module = get_module(module_name)
    if module:
        return object_map[module_name].get(object_type)

def get_object_class_or_404(*args, **kwargs):
    result = get_object_class(*args, **kwargs)
    if not result:
        return abort(404)

    return result


def get_object(module_name, object_type, object_id):
    object_class = get_object_class(module_name, object_type)
    return object_class.query.get(object_id)

def get_object_or_404(*args, **kwargs):
    result = get_object(*args, **kwargs)
    if not result:
        return abort(404)

    return result


def get_objects(module_name, object_type, *filters):
    object_class = get_object_class(module_name, object_type)
    return object_class.query.filter(*filters)
