# oxy.io
# File: oxyio/websockets/base.py
# Desc: base websocket class

import json

from oxyio.app import websocket_map
from oxyio.log import logger


class MetaWebsocket(type):
    '''
    Metaclass that attaches Websocket classes to websocket_map.
    '''

    def __init__(cls, name, bases, d):
        if name != 'Websocket':
            module_name, websocket_name = cls.NAME.split('/')

            # Map the websocket
            (websocket_map
                .setdefault(module_name, {})
            )[websocket_name] = cls

            logger.debug('Registered new websocket {0}/{1}'.format(
                module_name, websocket_name
            ))

        super(MetaWebsocket, cls).__init__(name, bases, d)


class Websocket:
    __metaclass__ = MetaWebsocket

    def __init__(self, data, ws):
        self.ws = ws

    def run_forever(self):
        while True:
            data = self.ws.receive()

            # Break when timeout or closed connection
            if data is None:
                break

            elif data:
                try:
                    data = json.loads(data)
                    self.on_event(data['event'], data['data'])

                # We ignore other websocket data (pings/etc)
                except ValueError:
                    logger.warning('Received dodgy websocket data: "{0}"'.format(data))

    def emit(self, event, data):
        '''Push an event down the websocket.'''

        self.ws.send(json.dumps({
            'event': event,
            'data': data
        }))

    # Ignore input by default
    def on_event(self, event, data):
        pass
