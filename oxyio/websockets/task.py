# oxy.io
# File: oxyio/websockets/task.py
# Desc: the task subscribe/watch websocket (Redis events -> websocket)

from oxyio import settings
from oxyio.util.pubsub import subscribe, unsubscribe

from .base import Websocket


class Subscribe(Websocket):
    '''Subscribes to a task via Redis pubsub & relays to client.'''

    NAME = 'core/task_subscribe'

    def __init__(self, data, ws):
        self.ws = ws

        channel_name = '{0}{1}'.format(settings.REDIS_TASK_PREFIX, data)

        # Subscribe to the task
        subscribe(self.on_task_event, channel=channel_name)

        # Wait until the websocket is closed
        self.run_forever()

        # Connection closed, let's unsusbscribe our function
        unsubscribe(self.on_task_event, channel=channel_name)

    def on_task_event(self, data):
        '''Forward incoming Redis events -> websocket, already JSON'd.'''

        self.ws.send(data)


class Admin(Websocket):
    '''Monitors & admins all running tasks.'''

    NAME = 'core/task_admin'
