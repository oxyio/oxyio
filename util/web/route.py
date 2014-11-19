# Oxypanel
# File: util/route.py
# Desc: flask's missing regex url router!
# massive thanks to ATOzTOA @ stackoverflow:
# http://stackoverflow.com/questions/14350920/define-a-route-for-url-ending-with-integer-in-python

from werkzeug.routing import BaseConverter
from flask import g

from app import app


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.url_value_preprocessor
def parse_url_module_object(endpoint, values):
    if isinstance(values, dict):
        if 'module_name' in values:
            g.module = values['module_name']
        if 'object_type' in values:
            g.object = values['object_type']
        if 'objects_type' in values:
            g.object = values['objects_type']
