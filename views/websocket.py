# Oxypanel
# File: views/webscoket.py
# Desc: the websocket request handler

from flask import request

import config
from app import app, websocket, redis_client
from util.data import get_websocket


# More internal router than view
@websocket.route('/websocket')
def websocket_request(ws):
    with app.request_context(ws.environ):
        # Get & verify request
        request_key = request.args.get('key', None)
        request_data = redis_client.hgetall(
            '{0}{1}'.format(config.REDIS['WEBSOCKET_REQUEST_PREFIX'], request_key)
        )

        if len(request_data) == 0:
            return ws.send('INVALID_REQUEST')

        user_id = request.args.get('user_id', None)
        if not user_id or request_data['user_id'] != user_id:
            return ws.send('INVALID_USER')

    # Looks like everything's OK, lets load the websocket in question
    module_name, websocket_name = request_data['websocket'].split('/')
    websocket_class = get_websocket(module_name, websocket_name)
    if websocket_class is None:
        return ws.send('INVALID_WEBSOCKET')

    # Start the websocket!
    websocket_class(request_data['websocket_data'], ws)
