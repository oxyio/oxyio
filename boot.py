# flake8: noqa
# oxy.io
# File: boot.py
# Desc: bootstraps oxy.io

import os

# Async all the things
from gevent import monkey
monkey.patch_all()

from flask import Blueprint

# Bootstrap the settings
from oxyio import settings
settings.load_module(os.environ.get('settings', 'settings'))

from oxyio.util.log import logger

# Import the base task/web apps
from oxyio.app import web_app, task_app, module_map

# Import core models/websockets/tasks
from oxyio.models import user, permission
from oxyio.websockets import task
from oxyio.tasks import update

# Load/import all modules
from oxyio.app.module_loader import list_modules, load_module
for name in list_modules():
    load_module(name)


def boot_web():
    '''Bootstraps ready for the webserver.'''

    # Webserver
    from flask_debugtoolbar import DebugToolbarExtension

    # Debug toolbar
    web_app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(web_app)

    # Load web inlucdes (middleware, template funcs, etc)
    from oxyio.includes.web import csrf , log, route, template, json_encoder

    # Load core web views
    from oxyio.views import dashboard, account, error, object, objects, websocket

    # Load admin web views
    from oxyio.views.admin import debug, logs, permissions, settings, users, dashboard, tasks

    # Make module blueprints
    for name, module in module_map.iteritems():
        # Make flask blueprint
        module_blueprint = Blueprint(name, name,
            url_prefix='/{0}'.format(name),
            static_folder='modules/{0}/static'.format(name),
            template_folder='modules/{0}/templates'.format(name)
        )

        # Apply custom module routes
        if hasattr(module.config, 'ROUTES'):
            for (url, methods, func) in module.config.ROUTES:
                logger.debug('[{0}] Adding module URL rule: {1} -> {2}'.format(name, url, func))
                module_blueprint.add_url_rule(url, methods=methods, view_func=func)

        # Register blueprint
        web_app.register_blueprint(module_blueprint)


def boot_task():
    '''Bootstraps ready for the task worker.'''

    # Pre-start a Monitor task
    from pytask import Monitor

    # Add & prep monitor task
    task_app.add_task(Monitor)
    task_app.pre_start_task('pytask/monitor')


try:
    import uwsgi
    boot_web()
except ImportError:
    pass
