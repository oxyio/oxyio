# oxy.io
# File: views/dashboard.py
# Desc: the global dashboard view

from flask import render_template

from oxyio.app import web_app
from oxyio.web.util.user import login_required


@web_app.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')
