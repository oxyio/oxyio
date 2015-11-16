# Oxypanel
# File: util/csrf.py
# Desc: csrf protection!

from uuid import uuid4

from flask import session, abort, request, Markup

from ...app import web_app


# Check all POST/PUT/DELETE's
# 403 on failure
@web_app.before_request
def csrf_check():
    # TODO: Check referrer matches us

    # Check a valid csrf_token was presented
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.pop('csrf_token', None)
        if not token or token != str(request.form.get('csrf_token')):
            abort(401)


# Generate/store CSRF tokens
def generate_csrf():
    if 'csrf_token' not in session:
        session['csrf_token'] = str(uuid4())

    return session['csrf_token']

web_app.jinja_env.globals['csrf_token'] = generate_csrf

# Template shortcut
def generate_csrf_input():
    token = generate_csrf()
    return Markup('<input type="hidden" name="csrf_token" value="{0}" />'.format(token))

web_app.jinja_env.globals['csrf_input'] = generate_csrf_input
