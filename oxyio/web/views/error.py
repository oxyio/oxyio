# oxy.io
# File: views/error.py
# Desc: error views

from flask import abort

from oxyio import settings
from oxyio.app import web_app
from oxyio.web.response import render_or_jsonify


def _handle_error_view(code, e):
    return render_or_jsonify(
        'error.html'.format(code),
        status=code,
        error=e.name,
        error_message=e.description
    ), code


@web_app.errorhandler(401)
def error_unauthorized(e):
    return _handle_error_view(401, e)


@web_app.errorhandler(403)
def error_forbidden(e):
    return _handle_error_view(403, e)


@web_app.errorhandler(404)
def error_not_found(e):
    return _handle_error_view(404, e)


@web_app.errorhandler(405)
def error_not_allowed(e):
    return _handle_error_view(405, e)


@web_app.errorhandler(500)
def error_server_error(e):
    return _handle_error_view(500, e)


if settings.DEBUG:
    @web_app.route('/error/401')
    def debug_unauthorized():
        abort(401)

    @web_app.route('/error/403')
    def debug_forbidden():
        abort(403)

    @web_app.route('/error/404')
    def debug_not_found():
        abort(404)

    @web_app.route('/error/405')
    def debug_not_allowed():
        abort(405)

    @web_app.route('/error/500')
    def debug_server_error():
        abort(500)
