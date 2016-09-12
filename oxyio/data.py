# oxy.io
# File: oxyio/data.py
# Desc: global loading of modules, objects, websockets & tasks

from flask import abort

from oxyio.app import module_map, object_map, websocket_map, task_map


def get_module(module_name):
    return module_map.get(module_name)


def get_module_or_404(module_name):
    result = get_module(module_name)
    if not result:
        return abort(404)

    return result


def get_websocket(module_name, websocket_name):
    return websocket_map.get(module_name, {}).get(websocket_name)


def get_task(module_name, task_name):
    return task_map.get(module_name, {}).get(task_name)


def get_object_class(module_name, object_type):
    return object_map.get(module_name, {}).get(object_type)


def get_object_class_or_404(module_name, object_type):
    result = get_object_class(module_name, object_type)
    if not result:
        return abort(404)

    return result


def get_object(module_name, object_type, object_id):
    object_class = get_object_class(module_name, object_type)
    if not object_class:
        return None

    obj = object_class.query.get(object_id)
    return obj


def get_object_or_404(module_name, object_type, object_id):
    result = get_object(module_name, object_type, object_id)
    if not result:
        return abort(404)

    return result


def get_objects(module_name, object_type, *filters):
    object_class = get_object_class(module_name, object_type)
    return object_class.query.filter(*filters)
