# Oxypanel
# File: views/error.py
# Desc: error views

from flask import render_template

from app import app


@app.errorhandler(403)
def error_not_authorized(e):
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
