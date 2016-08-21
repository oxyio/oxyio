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

    urls = []
    api_urls = []

    for url in web_app.url_map.iter_rules():
        if 'debugtoolbar' in url.endpoint or 'debug_toolbar' in url.endpoint:
            continue

        url_meta = (url, url.endpoint, url.methods - {'OPTIONS', 'HEAD'})

        if '_api' in url.endpoint:
            api_urls.append(url_meta)

        else:
            urls.append(url_meta)

    # Load settings and sort alphabetically
    sorted_settings = sorted((
        (key, getattr(settings, key))
        for key in dir(settings)
        if(isinstance(key, str) and key.isupper())
    ), key=lambda item: item[0])

    return render_or_jsonify('admin/debug.html',
        action='debug',
        modules=module_map,
        objects=object_map,
        websockets=websocket_map,
        items=item_map,
        tasks=task_map,
        urls=sorted(urls, key=itemgetter(0)),
        api_urls=sorted(api_urls, key=itemgetter(0)),
        settings=sorted_settings,
        module_configs={
            name: {
                key: getattr(module.config, key)
                for key in dir(module.config)
                if(isinstance(key, str) and key.isupper())
            }
            for name, module in module_map.iteritems()
        },
    )
