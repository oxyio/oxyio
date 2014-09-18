from flask import g

from app import app
from util.response import render_or_jsonify


@app.route('/admin/logs', methods=['GET'])
def admin_logs():
    g.module = 'admin'

    return render_or_jsonify('admin/logs.html',
        action='logs'
    )
