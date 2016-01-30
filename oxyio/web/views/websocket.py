# oxy.io
# File: oxyio/views/webscoket.py
# Desc: the websocket request handler

import json

from flask import request

from oxyio import settings
from oxyio.app import web_app, websocket_app, redis_client
from oxyio.data import get_websocket
from oxyio.log import logger
from oxyio.web.user import get_current_user


# More internal router than view
@websocket_app.route('/websocket')
def websocket_request(ws):
    # Wrap the entire websocket process within the Flask request context - this ensures
    # a separate database session for the websocket, and that websockets can use Flasks
    # request/g/etc objects.
    with web_app.request_context(ws.environ):
        # Check user
        user = get_current_user()
        if not user: return ws.send('INVALID_USER')
        # Check request key
        request_key = request.args.get('key', None)
        if not request_key: return ws.send('INVALID_REQUEST_KEY')

        request_data = redis_client.hgetall(
            '{0}{1}'.format(settings.REDIS_WEBSOCKET_PREFIX, request_key)
        )

        if not request_data:
            return ws.send('INVALID_REQUEST')

        if int(request_data['user_id']) != user.id:
            logger.warning('Invalid user_id ({0}) w/valid websocket request: {1}'.format(
                user.id, request_key)
            )
            return ws.send('INVALID_USER')

        # Looks like everything's OK, lets load the websocket in question
        module_name, websocket_name = request_data['websocket'].split('/')
        websocket_class = get_websocket(module_name, websocket_name)
        if websocket_class is None:
            logger.critical('Websocket class not found: {}'.format(websocket_class))
            return ws.send('INVALID_WEBSOCKET')

        # Start the websocket!
        data = json.loads(request_data['websocket_data'])
        websocket_class(data, ws)
