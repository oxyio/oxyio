# Oxypanel
# File: util/tasks.py
# Desc: manage tasks tasks via Redis

import json

import config
from app import redis_client


def _build_task(task_name, task_data, new=False):
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


# Stop a task
def stop_task(task_id):
    redis_client.publish('{0}{1}-control'.format(config.REDIS['TASK_PREFIX'], task_id), 'stop')


# Start or update an existing task
def start_update_task(task_id, task_name, task_data):
    task_exists = redis_client.sismember(config.REDIS['TASK_SET'], task_id)

    # Write task data
    redis_client.hmset(
        '{0}{1}'.format(config.REDIS['TASK_PREFIX'], task_id),
        _build_task(task_name, task_data, new=(not task_exists))
    )

    # If the task is active, send reload command
    if task_exists:
        redis_client.publish('{0}{1}-control'.format(config.REDIS['TASK_PREFIX'], task_id), 'reload')
    # Otherwise, push it onto the queue
    else:
        redis_client.lpush(config.REDIS['NEW_QUEUE'], task_id)
