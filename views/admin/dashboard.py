from flask import g

from app import app
from util.response import render_or_jsonify


@app.route('/admin', methods=['GET'])
def admin_dashboard():
    g.module = 'admin'

    return render_or_jsonify('admin/dashboard.html')
