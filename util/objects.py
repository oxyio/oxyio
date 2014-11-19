# Oxypanel
# File: util/objects.py
# Desc: global loading of modules & their objects

from flask import g, abort

from app import app, module_map, object_map


# Warm request object cache
@app.before_request
def prepare_objects_g():
    g.objects = {}


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
    # Cache?
    cache_key = '{0}-{1}-{2}'.format(module_name, object_type, object_id)
    cached = g.objects.get(cache_key)
    if isinstance(cached, bool):
        return cached

    object_class = get_object_class(module_name, object_type)
    if not object_class:
        return None

    obj = object_class.query.get(object_id)

    if obj:
        g.objects[cache_key] = obj
        return obj
    else:
        g.objects[cache_key] = None

def get_object_or_404(*args, **kwargs):
    result = get_object(*args, **kwargs)
    if not result:
        return abort(404)

    return result


def get_objects(module_name, object_type, *filters):
    object_class = get_object_class(module_name, object_type)
    return object_class.query.filter(*filters)
