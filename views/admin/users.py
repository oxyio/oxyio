# Oxypanel
# File: views/admin/users.py
# Desc: manage users

from flask import g, abort, request, url_for

from app import app, db
from models.user import User, UserGroup
from util.user import permissions_required
from util.response import render_or_jsonify, redirect_or_jsonify


def _get_user_or_404(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(404)

    return user

def _get_group_or_404(group_id):
    group = UserGroup.query.get(group_id)
    if not group:
        abort(404)

    return group


@app.route('/admin/users', methods=['GET'])
@permissions_required('Admin', 'AdminUsers')
def admin_users():
    g.module = 'admin'
    users = User.query
    groups = UserGroup.query.all()

    if 'user_group_id' in request.args and len(request.args['user_group_id']) > 0:
        users = users.filter(User.user_group_id==request.args['user_group_id'])
    if 'name' in request.args and len(request.args['name']) > 0:
        users = users.filter(User.name.like('%{0}%'.format(request.args['name'])))

    return render_or_jsonify('admin/users.html',
        action='users',
        users=users.all(),
        groups=groups
    )

@app.route('/admin/users/<int:user_id>', methods=['GET'])
@permissions_required('Admin', 'AdminUsers')
def admin_view_edit_user(user_id):
    g.module = 'admin'
    user = _get_user_or_404(user_id)
    groups = UserGroup.query.all()

    return render_or_jsonify('admin/user.html',
        action='users',
        user=user,
        groups=groups
    )

@app.route('/admin/users/<int:user_id>', methods=['POST'])
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

    db.session.add(user)
    db.session.commit()
    return redirect_or_jsonify(success='User updated')

@app.route('/admin/users/add', methods=['POST'])
@permissions_required('Admin', 'AdminUsers')
def admin_add_user():
    pass

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@permissions_required('Admin', 'AdminUsers')
def admin_delete_user(user_id):
    user = _get_user_or_404(user_id)

    db.session.delete(user)
    db.session.commit()
    return redirect_or_jsonify(
        url_for('admin_users'),
        success='User deleted'
    )


@app.route('/admin/groups', methods=['POST'])
@permissions_required('Admin', 'AdminUsers')
def admin_add_group():
    name = request.form.get('name')
    if not name or len(name) == 0:
        return redirect_or_jsonify(url_for('admin_users'), error='Invalid name')

    group = UserGroup()
    group.name = name

    db.session.add(group)
    db.session.commit()
    return redirect_or_jsonify(
        url_for('admin_users'),
        success='Group added'
    )

@app.route('/admin/groups/<int:group_id>', methods=['GET'])
@permissions_required('Admin', 'AdminUsers')
def admin_view_edit_group(group_id):
    g.module = 'admin'
    group = _get_group_or_404(group_id)

    return render_or_jsonify('admin/group.html',
        action='users',
        group=group
    )

@app.route('/admin/groups/<int:group_id>', methods=['POST', 'PUT'])
@permissions_required('Admin', 'AdminUsers')
def admin_edit_group(group_id):
    name = request.form.get('name')
    if not name or len(name) == 0:
        return redirect_or_jsonify(error='Invalid name')

    group = _get_group_or_404(group_id)
    group.name = name

    db.session.add(group)
    db.session.commit()
    return redirect_or_jsonify(success='Group updated')

@app.route('/admin/groups/<int:user_group_id>', methods=['DELETE'])
@permissions_required('Admin', 'AdminUsers')
def admin_delete_user_group(user_group_id):
    group = UserGroup.query.get(user_group_id)
    if not group:
        abort(404)

    db.session.delete(group)
    db.session.commit()
    redirect_or_jsonify(
        url_for('admin_user'),
        success='Group deleted'
    )
