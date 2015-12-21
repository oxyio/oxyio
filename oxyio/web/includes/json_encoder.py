# oxy.io
# File: oxyio/includes/web/json_encoder.py
# Desc: custom JSON encoder handling oxy.io object serialisatio

from flask.json import JSONEncoder

from oxyio.app import web_app


class OxyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'serialise'):
            return obj.serialise()

        super(OxyJSONEncoder, self).default(obj)


web_app.json_encoder = OxyJSONEncoder
