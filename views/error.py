# Oxypanel
# File: views/error.py
# Desc: error views

from flask import render_template, abort

import config
from app import app


@app.errorhandler(401)
def error_unauthorized(e):
    return render_template('error/401.html', error=e), 401

@app.errorhandler(403)
def error_forbidden(e):
    return render_template('error/403.html', error=e), 403

@app.errorhandler(404)
def error_not_found(e):
    return render_template('error/404.html', error=e), 404

@app.errorhandler(405)
def error_not_allowed(e):
    return render_template('error/405.html', error=e), 405

@app.errorhandler(500)
def error_server_error(e):
    return render_template('error/500.html', error=e), 500


if config.DEBUG:
    @app.route('/error/401')
    def debug_unauthorized():
        abort(401)

    @app.route('/error/403')
    def debug_forbidden():
        abort(403)

    @app.route('/error/404')
    def debug_not_found():
        abort(404)

    @app.route('/error/405')
    def debug_not_allowed():
        abort(405)

    @app.route('/error/500')
    def debug_server_error():
        abort(500)
