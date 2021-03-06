# oxy.io
# File: oxyio/views/account.py
# Desc: views for users (login,profile/etc)

import os
from hashlib import sha512

from sqlalchemy.orm import exc
from flask import render_template, redirect, request, session, url_for

from oxyio import settings
from oxyio.app import web_app, db
from oxyio.util import hash_password, check_password
from oxyio.models.user import User
from oxyio.web.user import get_current_user, login_required, is_logged_in
from oxyio.web.response import redirect_or_jsonify


@web_app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = get_current_user()

    # Remove session data
    session['session_key'] = None
    session['user_id'] = None

    # Remove key in db
    user.session_key = None
    db.session.add(user)
    db.session.commit()

    return redirect('/login')


@web_app.route('/login', methods=['GET'])
def view_login():
    if is_logged_in():
        return redirect('/')

    return render_template('login.html')

@web_app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if not (email or password):
        return redirect_or_jsonify(error='Please enter an email & password')

    # Find the user
    try:
        user = User.query.filter_by(email=email).one()
    except exc.NoResultFound:
        return redirect_or_jsonify(error='No user found')

    # Check the password against the one in db
    if not check_password(password.encode('utf-8'), user.password.encode('utf-8')):
        return redirect_or_jsonify(error='Invalid email/password combination')

    # We're in, lets login the user
    # Generate session_key
    key = sha512('{0}{1}'.format(os.urandom(32), settings.SECRET)).hexdigest()
    session['session_key'] = key # flasks "secure" sessions
    session['user_id'] = user.id

    # Save user
    user.session_key = key
    db.session.add(user)
    db.session.commit()

    return redirect(request.form.get('referrer', '/'))


@web_app.route('/reset-password', methods=['GET'])
def view_reset_password():
    return render_template('resetpw.html')


@web_app.route('/reset-password', methods=['POST'])
def reset_password():
    return redirect_or_jsonify(success='A reset email has been sent if this email exists')
    # Set key & time
    # Email user


@web_app.route('/profile', methods=['GET'])
@login_required
def view_profile():
    return render_template('profile.html')


@web_app.route('/profile', methods=['POST'])
@login_required
def edit_profile():
    user = get_current_user()

    for field in [
        'name',
        'email'
    ]:
        if field in request.form and len(request.form[field]) == 0:
            return redirect_or_jsonify(error='Invalid {0}'.format(field))
        else:
            setattr(user, field, request.form[field])

    # Password changed?
    if 'new_password' in request.form and len(request.form['new_password']) > 0:
        user.password = hash_password(request.form['new_password'])

    # Add, commit & redirect!
    db.session.add(user)
    db.session.commit()
    return redirect_or_jsonify(url_for('view_profile'), success='Profile updated')
