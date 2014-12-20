# Oxypanel
# File: util/web/cookie.py
# Desc: cookie setting helper

from flask import g

from app import app


@app.before_request
def prepare_cookies():
    g.set_cookies = {}
    g.delete_cookies = []


def set_cookie(key, value, **kwargs):
    g.set_cookies[key] = (unicode(value), kwargs)


def delete_cookie(key, **kwargs):
    g.delete_cookies.append((key, kwargs))


@app.after_request
def set_cookies(response):
    for key, (value, kwargs) in g.set_cookies.iteritems():
        response.set_cookie(key, value, **kwargs)

    for (key, kwargs) in g.delete_cookies:
        response.set_cookie(key, expires=0, **kwargs)

    return response
