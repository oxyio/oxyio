# oxy.io
# File: oxyio/views/admin/settings.py
# Desc: admin settings display

from flask import g

from ...app import web_app
from ...util.web.response import render_or_jsonify


@web_app.route('/admin/settings', methods=['GET'])
def admin_settings():
    g.module = 'admin'

    return render_or_jsonify('admin/settings.html',
        action='settings'
    )
