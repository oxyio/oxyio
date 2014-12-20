# Oxypanel
# File: views/admin/debug.py
# Desc: the debug view!

from operator import itemgetter

from flask import g

import config
from app import app, module_map, object_map, websocket_map, item_map, task_map
from util.web.response import render_or_jsonify
from util.web.user import permissions_required


@app.route('/admin/debug', methods=['GET'])
@permissions_required('Admin', 'AdminDebug')
def admin_debug():
    g.module = 'admin'

    return render_or_jsonify('admin/debug.html',
        action='debug',
        modules=module_map,
        objects=object_map,
        websockets=websocket_map,
        items=item_map,
        tasks=task_map,
        urls=sorted([
            (url, url.endpoint, url.methods - {'OPTIONS', 'HEAD'})
            for url in app.url_map.iter_rules()
            if 'debugtoolbar' not in url.endpoint and 'debug_toolbar' not in url.endpoint
        ], key=itemgetter(0)),
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
