# oxy.io
# File: oxyio/util/web/route.py
# Desc: handle automatic html/api routes & regex route for werkzeug
# massive thanks to ATOzTOA @ stackoverflow:
# http://stackoverflow.com/questions/14350920

from werkzeug.routing import BaseConverter
from flask import g, request

from oxyio.app import web_app


@web_app.before_request
def set_api_mode():
    g.api = request.endpoint and request.endpoint.startswith('api_')


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


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

web_app.url_map.converters['regex'] = RegexConverter


@web_app.url_value_preprocessor
def parse_url_module_object(endpoint, values):
    '''
    Push shared endpoint names (eg /module_name/objects_type) on to g for this request.
    '''
    if isinstance(values, dict):
        for key, attribute in [
            ('module_name', 'module'),
            ('object_type', 'object'),
            ('objects_type', 'object')
        ]:
            if key in values:
                setattr(g, attribute, values[key])
