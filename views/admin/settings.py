from flask import g

from app import app
from util.response import render_or_jsonify


@app.route('/admin/settings', methods=['GET'])
def admin_settings():
    g.module = 'admin'

    return render_or_jsonify('admin/settings.html',
        action='settings'
    )
