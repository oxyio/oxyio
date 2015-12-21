# oxy.io
# File: oxyio/util/web/request.py
# Desc: request utilities

from flask import g, request


def _parse_request_form():
    return {
        key: value[0] if len(value) == 1 else value
        for key, value in request.form.iterlists()
    }


def get_request_data():
    if not hasattr(g, 'request_data'):
        # The API accepts JSON
        if g.api:
            g.request_data = request.json()

        # Everywhere else, form data (parse out single values)
        else:
            g.request_data = _parse_request_form()

    return g.request_data


def in_request_args(field):
    return field in request.args and request.args[field]


def in_request_data(field):
    request_data = get_request_data()
    return field in request_data and request_data[field]
