# oxy.io
# File: oxyio/web/pubsub.py
# Desc: handles listening to pubsub events

import gevent

from oxyio.app import redis_client
from oxyio.log import logger


_pubsub = None

# Store internal subscription lists
_pattern_subscriptions = {}
_channel_subscriptions = {}


def _get_pubsub_message():
    message = _pubsub.get_message()

    if message:
        logger.debug('Pubsub message: {0}'.format(message))

        if message['type'] == 'pmessage':
            for callback in _pattern_subscriptions.get(message['pattern'], []):
                callback(message['data'])

        if message['type'] == 'message':
            for callback in _channel_subscriptions.get(message['channel'], []):
                callback(message['data'])

    return message


def _check_redis():
    '''Custom listen loop so we can subscribe 'on-demand'.'''

    while True:
        # Read messages until we have no more
        while _get_pubsub_message():
            pass

        gevent.sleep(.5)


def consume_messages():
    '''Start consuming messages from Redis.'''

    global _pubsub

    _pubsub = redis_client.pubsub()

    # Has to be called before we can get_message
    _pubsub.subscribe('oxypanel')
    gevent.spawn(_check_redis)


def subscribe(callback, channel=None, pattern=None):
    '''Subscribe to a channel and/or pattern, with a callback.'''

    if channel is not None:
        _channel_subscriptions.setdefault(channel, []).append(callback)

        # Subscribe via Redis
        logger.debug('Subscribing to channel: {0}'.format(channel))
        _pubsub.subscribe(channel)

    if pattern is not None:
        _pattern_subscriptions.setdefault(pattern, []).append(callback)

        # Subscribe via Redis
        logger.debug('Subscribing to pattern: {0}'.format(pattern))
        _pubsub.psubscribe(pattern)


def unsubscribe(callback, channel=None, pattern=None):
    '''Unsubscribe from a channel and/or pattern.'''

    if channel is not None and callback in _channel_subscriptions.get(channel, []):
        _channel_subscriptions[channel].remove(callback)

        # If there are now no callbacks for this channel, actually unsubscribe
        if not _channel_subscriptions[channel]:
            logger.debug('Unsubscribing from channel: {0}'.format(channel))
            _pubsub.unsubscribe(channel)

    if pattern is not None and callback in _pattern_subscriptions.get(pattern, []):
        _pattern_subscriptions[pattern].remove(callback)

        # If there are no callbacks for this pattern, actually unsubscribe
        if not _pattern_subscriptions[pattern]:
            logger.debug('Unsubscribing from pattern: {0}'.format(pattern))
            _pubsub.punsubscribe(pattern)
