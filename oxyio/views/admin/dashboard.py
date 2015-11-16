# oxy.io
# File: oxyio/views/admin/dashboard.py
# Desc: the admin dashboard view

from flask import g

from ...app import web_app
from ...util.web.response import render_or_jsonify


@web_app.route('/admin', methods=['GET'])
def admin_dashboard():
    g.module = 'admin'

    return render_or_jsonify('admin/dashboard.html')
