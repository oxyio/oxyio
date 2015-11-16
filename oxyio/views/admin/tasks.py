# oxy.io
# File: oxyio/views/admin/tasks.py
# Desc: view system tasks (in ES)

from flask import g

from ...app import web_app
from ...util.web.response import render_or_jsonify
from ...util.web.user import permissions_required
from ...util.web.flashes import flash_request
from ...util.web.websockets import make_websocket_request


@web_app.route('/admin/tasks', methods=['GET'])
@permissions_required('Admin', 'AdminLogs')
def admin_tasks():
    g.module = 'admin'

    # Create websocket request for task admin
    request_key = make_websocket_request('core/task_admin')
    flash_request('task_admin', request_key)

    return render_or_jsonify('admin/tasks.html',
        action='tasks'
    )
