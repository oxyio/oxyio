# oxyio
# File: oxyio/middleware/log.py
# Desc: log requests

from datetime import datetime

from flask import request

from oxyio.app import web_app


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
