# oxy.io
# File: oxyio/util/web/request.py
# Desc: request utilities

from flask import g, request

from oxyio.app import web_app, db


# Fixes teardown_request not being called in DEBUG
web_app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

@web_app.teardown_request
def rollback_on_exception(exception):
    if exception:
        db.session.rollback()

    db.session.remove()


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


def get_stat_request_kwargs():
    out = {}

    # Type is a special case, becomes type_
    if in_request_args('type'):
        out['type_'] = request.args['type']

    # Normal fields
    for field in ('interval', 'since', 'to', 'stat_type'):
        if in_request_args(field):
            out[field] = request.args[field]

    # Multi/terms fields (true = terms on all)
    for field in ('keys', 'details'):
        if in_request_args(field):
            item = request.args[field]

            if item == 'true':
                item = True

            elif ',' in item:
                item = item.split(',')

            out[field] = item

    return out
