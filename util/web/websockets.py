# Oxypanel
# File: util/web/websockets.py
# Desc: helpers to make authed websocket requests

from uuid import uuid4

import config
from app import redis_client
from util.web.user import get_current_user


def make_websocket_request(websocket, websocket_data):
    '''Generates a websocket request and puts it into Redis for the websocket view to handle'''
    request_key = str(uuid4())
    user = get_current_user()

    # Add Redis hash set for websocket processor
    redis_client.hmset(
        '{0}{1}'.format(config.REDIS['WEBSOCKET_REQUEST_PREFIX'], request_key), {
            'user_id': user.id,
            'websocket': websocket,
            'websocket_data': websocket_data
        }
    )

    return request_key
