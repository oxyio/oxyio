# Oxypanel
# File: views/admin/logs.py
# Desc: view system logs (in ES)

from flask import g

from app import app
from util.web.response import render_or_jsonify


@app.route('/admin/logs', methods=['GET'])
def admin_logs():
    g.module = 'admin'

    return render_or_jsonify('admin/logs.html',
        action='logs'
    )
