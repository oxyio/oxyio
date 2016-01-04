#!/usr/bin/env python
# flake8: noqa

# oxy.io
# File: boot.py
# Desc: bootstraps oxy.io

import os
import sys

# Async all the things
from gevent import monkey
monkey.patch_all()

from flask import Blueprint

# Bootstrap the settings
from oxyio import settings
settings.load_module(os.environ.get('settings', 'settings'))

from oxyio.util.log import logger

# Import the base task/web apps
from oxyio.app import web_app, task_app, module_map, task_map

# Load/import all modules
from oxyio.app.module_loader import load_module


def boot_core():
    '''Bootstraps/loads core models/websockets/tasks.'''

    logger.debug('Loading core')

    from oxyio.models import user, note
    from oxyio.websockets import task
    from oxyio.tasks import update


def boot_all_modules():
    '''Bootstraps/loads all the modules.'''

    for name in settings.MODULES:
        load_module(name)


def boot_web():
    '''Bootstraps the webserver.'''

    # Webserver
    from flask_debugtoolbar import DebugToolbarExtension

    # Debug toolbar
    web_app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(web_app)

    # Load web inlucdes (middleware, template funcs, etc)
    from oxyio.web.includes import csrf , log, route, template, json_encoder

    # Load core web views
    from oxyio.web.views import dashboard, account, error, object, objects, websocket

    # Load admin web views
    from oxyio.web.views.admin import (
        debug, logs, permissions, users, dashboard, tasks,
        settings as _settings
    )

    # Make module blueprints
    for name, module in module_map.iteritems():
        # Make flask blueprint
        module_blueprint = Blueprint(name, name,
            url_prefix='/{0}'.format(name),
            static_folder='modules/{0}/web/static'.format(name),
            template_folder='modules/{0}/web/templates'.format(name)
        )

        # Apply custom module routes
        if hasattr(module.config, 'ROUTES'):
            for (url, methods, func) in module.config.ROUTES:
                logger.debug('[{0}] Adding module URL rule: {1} -> {2}'.format(name, url, func))
                module_blueprint.add_url_rule(url, methods=methods, view_func=func)

        # Register blueprint
        web_app.register_blueprint(module_blueprint)


def run_web():
    '''Run uWSGI.'''

    web_app.run(app='boot:web_app', gevent=settings.GEVENT, port=settings.PORT)


def boot_task():
    '''Bootstraps the task worker.'''

    # Pre-start a Monitor task
    from pytask import Monitor

    # Add & prep monitor task
    task_app.add_task(Monitor)
    task_app.pre_start_task('pytask/monitor')

    for _, tasks in task_map.iteritems():
        for _, task_class in tasks.iteritems():
            task_app.add_task(task_class)


def run_task():
    '''Run pytask.'''

    task_app.run()


booter = runner = None

# Simple CLI implementation
if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'server':
            booter = boot_web
            runner = run_web
        elif sys.argv[1] == 'worker':
            booter = boot_task
            runner = run_task

    if booter is None:
        sys.stderr.write('Usage: ./boot.py [server|worker]\n')
        sys.exit(1)

# Otherwise try uWSGI
else:
    try:
        import uwsgi
        booter = boot_web
    except ImportError:
        pass


# Bootstrapping?
if booter:
    boot_core()
    boot_all_modules()
    booter()

# Running something?
if runner:
    runner()
