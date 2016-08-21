# oxy.io
# File: oxyio/views/admin/users.py
# Desc: manage users

from flask import g, abort, request, url_for

from oxyio.app import web_app, db
from oxyio.util import hash_password
from oxyio.models.user import User, UserGroup
from oxyio.web.user import permissions_required
from oxyio.web.response import render_or_jsonify, redirect_or_jsonify


def _get_user_or_404(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)

    return user


@web_app.route('/admin/users', methods=['GET'])
@permissions_required('Admin', 'AdminUsers')
def admin_users():
    g.module = 'admin'
    users = User.query
    groups = UserGroup.query.all()

    filtered = False

    if 'user_group_id' in request.args and len(request.args['user_group_id']) > 0:
        users = users.filter(User.user_group_id == request.args['user_group_id'])
        filtered = True

    if 'name' in request.args and len(request.args['name']) > 0:
        users = users.filter(User.name.like('%{0}%'.format(request.args['name'])))
        filtered = True

    return render_or_jsonify(
        'admin/users.html',
        action='users',
        users=users.all(),
        groups=groups,
        filtered=filtered,
    )


@web_app.route('/admin/users/<int:user_id>/edit', methods=['GET'])
@permissions_required('Admin', 'AdminUsers')
def admin_view_edit_user(user_id):
    g.module = 'admin'
    user = _get_user_or_404(user_id)
    groups = UserGroup.query.all()

    return render_or_jsonify(
        'admin/user.html',
        action='users',
        user=user,
        groups=groups,
    )


@web_app.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@permissions_required('Admin', 'AdminUsers')
def admin_edit_user(user_id):
    user = _get_user_or_404(user_id)

    # We generally trust admins, and validate nothing
    # note invalid user_groups will be rejected by MySQL
    for field in [
        'name',
        'email'
    ]:
        if field in request.form:
            setattr(user, field, request.form.get(field))

    if 'user_group_id' in request.form:
        user.user_group_id = int(request.form['user_group_id'])
        if user.user_group_id == 0:
            user.user_group_id = None

    if 'is_keymaster' in request.form and request.form['is_keymaster'] == 'on':
        user.is_keymaster = True

    if 'new_password' in request.form and len(request.form['new_password']) > 0:
        user.password = hash_password(request.form['new_password'])

    db.session.add(user)
    db.session.commit()

    return redirect_or_jsonify(success='User updated')


@web_app.route('/admin/users', methods=['POST'])
@permissions_required('Admin', 'AdminUsers')
def admin_add_user():
    email = request.form['email']
    if len(email) == 0:
        return redirect_or_jsonify(error='Invalid email')

    user = User(email)
    db.session.add(user)
    db.session.commit()

    return redirect_or_jsonify(
        url_for('admin_edit_user', user_id=user.id),
        success='User added',
    )


@web_app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@permissions_required('Admin', 'AdminUsers')
def admin_delete_user(user_id):
    user = _get_user_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect_or_jsonify(
        url_for('admin_users'),
        success='User deleted',
    )
