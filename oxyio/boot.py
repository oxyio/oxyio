#!/usr/bin/env python

# oxy.io
# File: boot.py
# Desc: bootstraps & starts oxy.io servers/workers

from os import path, environ

# Async all the things
from gevent import monkey
monkey.patch_all()

from flask import Blueprint

# Bootstrap the settings
from oxyio import settings
settings.ROOT = path.dirname(path.abspath(__file__))
settings_module = environ.get('OXIO_SETTINGS', 'settings')
settings.load_module(settings_module)

from oxyio.log import logger

# Import the base task/web apps
from oxyio.app import web_app, task_app, module_map, task_map

# Load/import all modules
from oxyio.app.module_loader import load_module


def boot_core():
    '''Bootstraps/loads core models/websockets/tasks.'''

    logger.debug('Loading core')

    from oxyio.models import user, note  # noqa
    from oxyio.websockets import task  # noqa
    from oxyio.tasks import update, index  # noqa


def boot_all_modules():
    '''Bootstraps/loads all the modules.'''

    for name in settings.MODULES:
        load_module(name)


def boot_manage():
    '''Bootstraps the manager.'''

    from oxyio.scripts import user, database  # noqa


def run_manage():
    '''Run management.'''

    from flask.ext.script import Shell

    from oxyio.app import manager

    manager.add_command('shell', Shell())
    manager.run()


def boot_web():
    '''Bootstraps the webserver.'''

    # Debug toolbar
    from flask_debugtoolbar import DebugToolbarExtension
    web_app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(web_app)

    # Start pubsub consumer
    from oxyio.web.pubsub import consume_messages
    consume_messages()

    # Load web inlucdes (middleware, template funcs, etc)
    from oxyio.web import csrf, log, route, template, json_encoder  # noqa

    # Load core web views
    from oxyio.web.views import (  # noqa
        dashboard, account, error, object, objects, websocket
    )

    # Load admin web views
    from oxyio.web.views.admin import (  # noqa
        debug, logs, permissions, users, dashboard, tasks,
        settings as _settings
    )

    # Make module blueprints
    for name, module in module_map.iteritems():
        # Make flask blueprint
        module_blueprint = Blueprint(name, name,
            url_prefix='/{0}'.format(name),
            static_folder='{0}/{1}/web/static'.format(web_app.root_path, name),
            template_folder='{0}/{1}/web/templates'.format(web_app.root_path, name)
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

    web_app.run(
        app='oxyio.boot:web_app',
        gevent=settings.GEVENT,
        port=settings.PORT,
        lazy=True,
        **{
            # Make uWSGI fail if it can't load the app
            'need-app': True
        }
    )


def boot_task():
    '''Bootstraps the task worker.'''

    # Pre-start Monitor & Cleanup tasks
    from pytask.tasks import Monitor, Cleanup
    task_app.add_tasks(Monitor, Cleanup)
    task_app.start_local_task('pytask/monitor')
    task_app.start_local_task(
        'pytask/cleanup',
        task_handler='oxyio.tasks.log:log_task'
    )

    # Start an indexer task
    task_app.start_local_task('core/index_stats')

    for _, tasks in task_map.iteritems():
        for _, task_class in tasks.iteritems():
            task_app.add_task(task_class)


def run_task():
    '''Run pytask.'''

    task_app.run()


def boot(booter=None, runner=None):
    # Bootstrapping?
    if booter:
        boot_core()
        boot_all_modules()
        booter()

    # Running something?
    if runner:
        runner()


# Catch uWSGI reloads
uwsgi = None

try:
    import uwsgi  # noqa
except ImportError:
    pass

if uwsgi:
    boot(boot_web)
