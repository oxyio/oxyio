# Oxypanel
# File: views/account.py
# Desc: views for users (login,profile/etc)

import os
from hashlib import sha512

from sqlalchemy.orm import exc
from flask import render_template, redirect, request, session, url_for

import config
from app import app, db
from models.user import User
from util.web.user import check_password, get_current_user, login_required, is_logged_in
from util.web.response import redirect_or_jsonify
from util.web.cookie import set_cookie, delete_cookie


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = get_current_user()

    # Remove session data
    session['session_key'] = None
    delete_cookie('user_id')

    # Remove key in db
    user.session_key = None
    db.session.add(user)
    db.session.commit()

    return redirect('/login')


@app.route('/login', methods=['GET'])
def view_login():
    if is_logged_in():
        return redirect('/')

    return render_template('login.html')

@app.route('/login', methods=['POST'])
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
    except exc.exc.MultipleResultsFound:
        return redirect_or_jsonify(error='More than one user found')

    # Check the password against the one in db
    if not check_password(password.encode('utf-8'), user.password.encode('utf-8')):
        return redirect_or_jsonify(error='Invalid email/password combination')

    # We're in, lets login the user
    # Generate session_key
    key = sha512('{0}{1}'.format(os.urandom(32), config.SECRET)).hexdigest()
    session['session_key'] = key # flasks "secure" sessions
    # User ID is public (used in JS for websockets)
    set_cookie('user_id', user.id, max_age=(3600 * 24 * 365 * 10))

    # Save user
    user.session_key = key
    db.session.add(user)
    db.session.commit()

    return redirect(request.form.get('referrer', '/'))


@app.route('/resetpw', methods=['GET'])
def view_resetpw():
    return render_template('resetpw.html')

@app.route('/resetpw', methods=['POST'])
def resetpw():
    return redirect_or_jsonify(success='A reset email has been sent if this email exists')
    # Set key & time
    # Email user


@app.route('/profile', methods=['GET'])
@login_required
def view_profile():
    return render_template('profile.html')

@app.route('/profile', methods=['POST'])
@login_required
def edit_profile():
    user = get_current_user()

    for field in [
        'name',
        'email'
    ]:
        if field in request.form and len(request.form[field]) == 0:
            return redirect_or_jsonify(error='Invalid {0}'.format(field))

    user.name = request.form['name']
    user.email = request.form['email']

    # Add, commit & redirect!
    db.session.add(user)
    db.session.commit()
    return redirect_or_jsonify(url_for('view_profile'), success='Profile updated')
