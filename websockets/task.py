# Oxypanel
# File: websockets/task.py
# Desc: the task subscribe/watch websocket (Redis events -> websocket)

import config
from models.websocket import Websocket
from util.web.pubsub import subscribe


class Subscribe(Websocket):
    '''Subscribes to a task via Redis pubsub & relays to client'''
    NAME = 'core/task_subscribe'

    def __init__(self, data, ws):
        self.ws = ws

        # Subscribe to the task
        subscribe(self._on_data, channel='{0}{1}'.format(
            config.REDIS_TASK_PREFIX,
            data
        ))

        # Keeps the websocket open
        self.run_forever()

    def _on_data(self, data):
        '''Forward incoming Redis events -> websocket, already JSON'd'''
        self.ws.send(data)


class Admin(Websocket):
    '''Monitors & admins all running tasks'''
    NAME = 'core/task_admin'
