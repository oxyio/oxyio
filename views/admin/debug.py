# Oxypanel
# File: views/admin/debug.py
# Desc: the debug view!

from flask import g

import config
from app import app, module_map, object_map
from util.web.response import render_or_jsonify
from util.user import permissions_required


@app.route('/admin/debug', methods=['GET'])
@permissions_required('Admin', 'AdminDebug')
def admin_debug():
    g.module = 'admin'

    return render_or_jsonify('admin/debug.html',
        action='debug',
        modules=module_map,
        objects=object_map,
        urls={
            url: {
                'endpoint': url.endpoint,
                'methods': url.methods - {'OPTIONS', 'HEAD'}
            }
            for url in app.url_map.iter_rules()
            if 'debugtoolbar' not in url.endpoint and 'debug_toolbar' not in url.endpoint
        },
        configs={
            key: getattr(config, key)
            for key in dir(config)
            if(isinstance(key, str) and key.isupper())
        },
        module_configs={
            name: {
                key: getattr(module.config, key)
                for key in dir(module.config)
                if(isinstance(key, str) and key.isupper())
            }
            for name, module in module_map.iteritems()
        }
    )
