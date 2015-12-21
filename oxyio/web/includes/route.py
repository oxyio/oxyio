# oxy.io
# File: oxyio/includes/web/route.py
# Desc: flask's missing regex url router!
# massive thanks to ATOzTOA @ stackoverflow:
# http://stackoverflow.com/questions/14350920

from werkzeug.routing import BaseConverter
from flask import g, request

from oxyio.app import web_app


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


@web_app.before_request
def set_api_mode():
    g.api = request.endpoint and request.endpoint.startswith('api_')
