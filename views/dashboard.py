# Oxypanel
# File: views/dashboard.py
# Desc: the global dashboard view

from flask import render_template

from app import app
from util.user import login_required


@app.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')
