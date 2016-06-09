# oxy.io
# File: oxyio/util/web/route.py
# Desc: handle automatic html/api routes & regex route for werkzeug
# massive thanks to ATOzTOA @ stackoverflow:
# http://stackoverflow.com/questions/14350920

from flask import g, request

from oxyio.app import web_app


@web_app.before_request
def set_api_mode():
    g.api = request.endpoint and request.endpoint.startswith('api_')


def html_api_route(url, **kwargs):
    def decorator(func):
        func_name = kwargs.pop('endpoint', func.__name__)

        target_app = kwargs.pop('app', web_app)
        target_api_app = kwargs.pop('api_app', web_app)

        # Add both to the web app
        for app in (target_app, target_api_app):
            app.add_url_rule(url, func_name, func, **kwargs)

        return func
    return decorator
