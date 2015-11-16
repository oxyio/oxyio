# oxy.io
# File: oxyio/util/web/pubsub.py
# Desc: handles listening to pubsub events for web(sockets)

import gevent

from ...app import redis_client
from ..log import logger

_pubsub = redis_client.pubsub()

# Store internal subscription lists
_pattern_subscriptions = {}
_channel_subscriptions = {}


def check_redis():
    '''Custom listen loop so we can subscribe 'on-demand'''
    while True:
        message = _pubsub.get_message()

        if message and message['type'] == 'message':
            logger.debug('Pubsub message: {0}'.format(message))

            if message['pattern'] in _pattern_subscriptions:
                for callback in _pattern_subscriptions[message['pattern']]:
                    callback(message['data'])

            if message['channel'] in _channel_subscriptions:
                for callback in _channel_subscriptions[message['channel']]:
                    callback(message['data'])

            # Check for additional messages
            check_redis()
        gevent.sleep(.5)

_pubsub.subscribe('oxypanel') # Has to be called before we can get_message
gevent.spawn(check_redis)


def subscribe(callback, channel=None, pattern=None):
    '''Subscribe to a channel and/or pattern, with a callback'''
    if channel is not None:
        logger.debug('Subscribing to channel: {}'.format(channel))
        _channel_subscriptions.setdefault(channel, []).append(callback)
        _pubsub.subscribe(channel)

    if pattern is not None:
        logger.debug('Subscribing to pattern: {}'.format(pattern))
        _pattern_subscriptions.setdefault(pattern, []).append(callback)
        _pubsub.psubscribe(pattern)
