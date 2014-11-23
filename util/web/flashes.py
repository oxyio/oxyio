# Oxypanel
# File: util/web/flashes.py
# Desc: like Flask's flash messages, we do one-time websocket request ID flashes

from flask import session


def get_flashed_request(name):
    return session.get('request_flashes', {}).pop(name, None)

# Name for link <> template
def flash_request(name, request_id):
    if 'request_flashes' not in session:
        session['request_flashes'] = {}

    session['request_flashes'][name] = request_id
