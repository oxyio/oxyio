# Oxypanel
# File: util/web/websockets.py
# Desc: helpers to make authed websocket requests

import json
from uuid import uuid4

from ... import settings
from ...app import redis_client
from ...util.web.user import get_current_user


def make_websocket_request(websocket, websocket_data=None):
    '''Generates a websocket request and puts it into Redis for the websocket view to handle'''
    if websocket_data is None: websocket_data = {}

    request_key = str(uuid4())
    user = get_current_user()

    # Add Redis hash set for websocket processor
    redis_client.hmset(
        '{0}{1}'.format(settings.REDIS_WEBSOCKET_PREFIX, request_key), {
            'user_id': user.id,
            'websocket': websocket,
            'websocket_data': json.dumps(websocket_data)
        }
    )

    return request_key
