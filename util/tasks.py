# Oxypanel
# File: util/tasks.py
# Desc: manage tasks tasks via Redis

import json
from uuid import uuid4

import config
from app import redis_client


def _build_task(task_name, task_data):
    data = {
        'function': task_name,
        'data': json.dumps(task_data)
    }

    return data


# Get list of active task_ids
def get_task_ids():
    return redis_client.sgetall(config.REDIS['TASK_SET'])


# Get a task & it's relevant data
def get_task(task_id):
    task_exists = redis_client.sismember(config.REDIS['TASK_SET'], task_id)

    if task_exists:
        # Get the task
        task = redis_client.hgetall('{0}{1}'.format(config.REDIS['TASK_PREFIX'], task_id))
        task.update({
            'id': task_id
        })

        return task


def _set_task(task_id, task_name, task_data):
    # Write task data
    redis_client.hmset(
        '{0}{1}'.format(config.REDIS['TASK_PREFIX'], task_id),
        _build_task(task_name, task_data)
    )

# Start a new task
def start_task(task_id, task_name, task_data):
    # This implies a non-long-running task
    # thus no option in start_upate
    if task_id is None:
        task_id = str(uuid4())

    _set_task(task_id, task_name, task_data)
    redis_client.lpush(config.REDIS['NEW_QUEUE'], task_id)

    return task_id


# Start or update an existing task
def start_update_task(task_id, task_name, task_data):
    task_exists = redis_client.sismember(config.REDIS['TASK_SET'], task_id)

    # If the task is active, send reload command
    if task_exists:
        # Update task hash
        _set_task(task_id, task_name, task_data)

        redis_client.publish(
            '{0}{1}-control'.format(config.REDIS['TASK_PREFIX'], task_id),
            'reload'
        )
    # Otherwise, push it onto the queue
    else:
        return start_task(task_id, task_name, task_data)


# Stop a task
def stop_task(task_id):
    redis_client.publish(
        '{0}{1}-control'.format(config.REDIS['TASK_PREFIX'], task_id),
        'stop'
    )
