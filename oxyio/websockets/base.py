# oxy.io
# File: oxyio/models/websocket.py
# Desc: base websocket class

from ..app import websocket_map


class MetaWebsocket(type):
    '''Metaclass that attaches Websocket classes to websocket_map.'''

    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)

        if name != 'Websocket':
            module_name, websocket_name = cls.NAME.split('/')
            websocket_map[module_name][websocket_name] = cls


class Websocket:
    __metaclass__ = MetaWebsocket

    # Useful for websockets which only push data to the client, so need to remain
    # open while waiting on callbacks
    def run_forever(self):
        while True:
            data = self.ws.receive()

            # Break when timeout or closed connection
            if data is None:
                break
            else:
                self.on_data(data)

    # Ignore input by default
    def on_data(self, data):
        pass
