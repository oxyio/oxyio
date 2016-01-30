# oxy.io
# File: views/error.py
# Desc: error views

from flask import render_template, abort

from oxyio import settings
from oxyio.app import web_app


@web_app.errorhandler(401)
def error_unauthorized(e):
    return render_template('error/401.html', error=e), 401

@web_app.errorhandler(403)
def error_forbidden(e):
    return render_template('error/403.html', error=e), 403

@web_app.errorhandler(404)
def error_not_found(e):
    return render_template('error/404.html', error=e), 404

@web_app.errorhandler(405)
def error_not_allowed(e):
    return render_template('error/405.html', error=e), 405

@web_app.errorhandler(500)
def error_server_error(e):
    return render_template('error/500.html', error=e), 500


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
