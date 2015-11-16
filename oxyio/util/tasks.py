# Oxypanel
# File: oxyio/util/tasks.py
# Desc: manage tasks tasks via Redis
#       this is done asynchronously via Redis pubsub (stop/update) or a queue (start)
#       this means start/stop/update functions don't validate/return a True/False

import json
from uuid import uuid4

from .. import settings
from ..app import redis_client


def _build_task(task_name, task_data):
    data = {
        'task': task_name,
        'data': json.dumps(task_data)
    }

    return data


def get_task_ids():
    '''Get a list of active task_ids'''
    return redis_client.sgetall(settings.REDIS_TASK_SET)


def get_task(task_id):
    '''Get a task & it's relevant data'''
    task_exists = redis_client.sismember(settings.REDIS_TASK_SET, task_id)

    if task_exists:
        # Get the task
        task = redis_client.hgetall('{0}{1}'.format(settings.REDIS_TASK_PREFIX, task_id))
        task.update({
            'id': task_id
        })

        return task


def _set_task(task_id, task_name, task_data):
    # Write task data
    redis_client.hmset(
        '{0}{1}'.format(settings.REDIS_TASK_PREFIX, task_id),
        _build_task(task_name, task_data)
    )


def start_task(task_id, task_name, task_data):
    '''Start a new task'''
    # task_id None implies a non-long-running task, thus no option in start_upate
    if task_id is None:
        task_id = str(uuid4())

    _set_task(task_id, task_name, task_data)
    redis_client.lpush(settings.REDIS_NEW_QUEUE, task_id)

    return task_id


def start_update_task(task_id, task_name, task_data):
    '''Start or update an existing task'''
    task_exists = redis_client.sismember(settings.REDIS_TASK_SET, task_id)

    # If the task is active, send reload command
    if task_exists:
        # Update task hash
        _set_task(task_id, task_name, task_data)

        redis_client.publish(
            '{0}{1}-control'.format(settings.REDIS_TASK_PREFIX, task_id),
            'reload'
        )
    # Otherwise, push it onto the queue
    else:
        start_task(task_id, task_name, task_data)


def stop_task(task_id):
    '''Stop a task'''
    redis_client.publish(
        '{0}{1}-control'.format(settings.REDIS_TASK_PREFIX, task_id),
        'stop'
    )
