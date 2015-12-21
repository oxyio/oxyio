# oxy.io
# File: oxyio/util/web/route.py
# Desc: handle automatic html/api routes

from oxyio.app import web_app


def html_api_route(html_endpoint, **kwargs):
    def decorator(func):
        # Generate equivalent API endpoint
        api_endpoint = '/api/v1{0}'.format(html_endpoint)
        api_name = 'api_{0}'.format(func.__name__)

        # Add both to the web app
        for endpoint, name in [
            (html_endpoint, func.__name__),
            (api_endpoint, api_name)
        ]:
            web_app.add_url_rule(endpoint, name, func, **kwargs)

        return func
    return decorator
