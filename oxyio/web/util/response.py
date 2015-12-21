# oxy.io
# File: oxio/util/web/response.py
# Desc: useful response fucntions

from flask import g, request, redirect, flash, jsonify, render_template


def redirect_or_jsonify(url=None, **kwargs):
    '''Redirect and pass messages or output JSON messages.'''

    if url is None:
        url = request.url

    # Add messages
    for category, message in kwargs.iteritems():
        flash(message, category)

    return redirect(url)


def render_or_jsonify(template, _template_data=None, **kwargs):
    '''Render a HTML template or output JSON data.'''

    if g.api:
        return jsonify(**kwargs)

    # Data only for the template
    if _template_data:
        kwargs.update(_template_data)

    return render_template(template, **kwargs)
