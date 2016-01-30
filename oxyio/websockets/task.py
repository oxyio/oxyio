# oxy.io
# File: oxyio/websockets/task.py
# Desc: the task subscribe/watch websocket (Redis events -> websocket)

import gevent
from pytask.helpers import run_loop

from oxyio.app import task_app
from oxyio.web.pubsub import subscribe, unsubscribe

from .base import Websocket


class Subscribe(Websocket):
    '''Subscribes to a task via Redis pubsub & relays to client.'''

    NAME = 'core/task_subscribe'

    def __init__(self, task_id, ws):
        super(Subscribe, self).__init__(task_id, ws)

        channel_name = task_app.helpers.task_key(task_id)
        task = task_app.helpers.get_task(task_id)

        # If the task has already ended, forward what we can and exit
        if task.get('state') not in ('RUNNING', 'WAIT'):
            self.emit(
                # If state isn't present, we should _assume_ the task failed somehow
                task.get('state', 'exception').lower(),
                task.get('output')
            )

            return

        # Subscribe to the task
        subscribe(self.on_task_event, channel=channel_name)

        # Wait until the websocket is closed
        self.run_forever()

        # Connection closed, let's unsusbscribe our function
        unsubscribe(self.on_task_event, channel=channel_name)

    def on_task_event(self, data):
        '''Forward incoming Redis events -> websocket, already JSON'd.'''

        # Data coming from pytask workers is already in the JSON format {event, data}, so
        # we needn't re-encode by using `self.emit`.
        self.ws.send(data)


class Admin(Websocket):
    '''Monitors & admins all running tasks.'''

    NAME = 'core/task_admin'

    def __init__(self, task_id, ws):
        super(Admin, self).__init__(task_id, ws)

        # Get all task messages from Redis pubsub
        pattern = '{0}*'.format(task_app.TASK_PREFIX)
        subscribe(self.on_tasks_event, pattern=pattern)

        # Create loop to periodically send down all task info
        loop = gevent.spawn(run_loop, self.send_tasks, 10)

        # Wait until websocket closes
        self.run_forever()

        # Unsubscribe
        unsubscribe(self.on_tasks_event, pattern=pattern)

        # Stop loop
        loop.kill()

    def on_tasks_event(self, data):
        # These messages are in the JSON format {event, data}, so will be "double wrapped"
        # inside a "task_message" event (specific to the TaskAdmin component).
        self.emit('task_message', data)

    def send_tasks(self):
        # Get task ID info
        active_task_ids = task_app.helpers.get_active_task_ids()
        new_task_ids = task_app.helpers.get_new_task_ids()
        end_task_ids = task_app.helpers.get_end_task_ids()

        # Get actual task info
        tasks = {
            task_id: task_app.helpers.get_task(task_id)
            for task_id in (active_task_ids + new_task_ids + end_task_ids)
        }

        # Push the info down the websocket
        self.emit('active_tasks', active_task_ids)
        self.emit('new_tasks', new_task_ids)
        self.emit('end_tasks', end_task_ids)
        self.emit('tasks', tasks)
