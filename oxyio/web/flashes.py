# oxy.io
# File: oxyio/util/web/flashes.py
# Desc: like Flask's flash messages, we do one-time websocket request ID flashes

from flask import session


def flash_task_subscribe(task_id):
    '''
    Pushes a task_subscribe request ID into the clients session. These ones are
    automatically shown at the top of pages in ``base.html`` (like flashed messages).
    '''

    session.setdefault('task_subscribe_flashes', []).append(task_id)


def get_flashed_task_subscribes():
    '''Get all the task subscribe requests.'''

    return session.pop('task_subscribe_flashes', [])


def get_flashed_request(name):
    '''Get a flashed request.'''

    return session.get('request_flashes', {}).pop(name, None)


def flash_request(name, request_id):
    '''
    Pushes named a request ID into the clients session. These are for specific things,
    like the device status or task list websockets, and templates specifically call them.
    '''

    session.setdefault('request_flashes', {})[name] = request_id
