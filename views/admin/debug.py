# Oxypanel
# File: views/admin/debug.py
# Desc: the debug view!

from flask import g

import config
from app import app, module_map, object_map
from util.response import render_or_jsonify
from util.user import permissions_required


@app.route('/admin/debug', methods=['GET'])
@permissions_required('Admin', 'AdminDebug')
def admin_debug():
    g.module = 'admin'

    return render_or_jsonify('admin/debug.html',
        action='debug',
        modules=module_map,
        objects=object_map,
        urls=app.url_map,
        configs={k: getattr(config, k) for k in dir(config) if(isinstance(k, str) and k.isupper())}
    )
