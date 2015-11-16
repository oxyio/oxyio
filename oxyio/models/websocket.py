# Oxypanel
# File: models/websocket.py
# Desc: base websocket with metaclass to transparently add to global map

from ..app import websocket_map


class MetaWebsocket(type):
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
            # Non-blocking/gevent
            data = self.ws.receive()
            # Break when timeout or closed connection
            if data is None:
                break
