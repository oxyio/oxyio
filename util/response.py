# Oxypanel
# File: util/response.py
# Desc: useful response fucntions

from flask import request, jsonify, redirect, flash, render_template


def redirect_or_jsonify(url=None, **kwargs):
    if url is None:
        url = request.url

    # POST = non-API mode
    if request.method == 'POST':
        # Add messages
        for category, message in kwargs.iteritems():
            flash(message, category)

        return redirect(url)
    else:
        return jsonify(**kwargs)


def render_or_jsonify(template, **kwargs):
    # If returning API and we're a POST/PUT/DELETE, include new csrf_token
    # old token already verified & removed in @before_request csrf_check

    return render_template(template, **kwargs)
