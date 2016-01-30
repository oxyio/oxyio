# oxy.io
# File: oxyio/views/admin/debug.py
# Desc: the debug view!

from operator import itemgetter

from flask import g

from oxyio import settings
from oxyio.app import web_app, module_map, object_map, websocket_map, item_map, task_map
from oxyio.web.response import render_or_jsonify
from oxyio.web.user import permissions_required


@web_app.route('/admin/debug', methods=['GET'])
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
            for url in web_app.url_map.iter_rules()
            if 'debugtoolbar' not in url.endpoint and 'debug_toolbar' not in url.endpoint
        ], key=itemgetter(0)),
        configs={
            key: getattr(settings, key)
            for key in dir(settings)
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
