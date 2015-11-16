# Oxypanel
# File: util/web/response.py
# Desc: useful response fucntions

from datetime import datetime

from flask import request, redirect, flash, render_template

from ...app import web_app


@web_app.after_request
def log_request(response):
    log = {
        'date': datetime.now(),
        'remote_ip': request.remote_addr,
        'request_method': request.method,
        'request_url': request.url,
        'request_headers': request.headers,
        'request_body': request.data,
        'response_headers': response.headers,
        'response_status': response.status_code
    }
    log

    # print log
    # print 'WRITE THIS INTO ES ^^^^^^^^^^^^^^'
    print 'write log to ES util/web/response.py'
    return response


def redirect_or_jsonify(url=None, **kwargs):
    if url is None:
        url = request.url

    # Add messages
    for category, message in kwargs.iteritems():
        flash(message, category)

    return redirect(url)


def render_or_jsonify(template, **kwargs):
    # If returning API and we're a POST/PUT/DELETE, include new csrf_token
    # old token already verified & removed in @before_request csrf_check

    return render_template(template, **kwargs)
