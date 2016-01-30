# oxy.io
# File: oxyio/views/admin/logs.py
# Desc: view system logs (in ES)

from flask import g

from oxyio.app import web_app
from oxyio.web.response import render_or_jsonify
from oxyio.web.user import permissions_required


@web_app.route('/admin/logs', methods=['GET'])
@permissions_required('Admin', 'AdminLogs')
def admin_logs():
    g.module = 'admin'

    return render_or_jsonify('admin/logs.html',
        action='logs'
    )
