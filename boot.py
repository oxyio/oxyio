#!/usr/bin/env python

# Oxypanel
# File: boot.py
# Desc: bootstrap Oxypanel modules/objects
#       entry point for: web | task

APPS = ['web', 'task']

import sys
if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in APPS:
        print 'Usage: boot.py {0}'.format(APPS)
        sys.exit(1)

from os import listdir, path
from glob import glob
from importlib import import_module

# Async all the things
from gevent import monkey
monkey.patch_all()

# Import config
import config
# What are we attempting to boot?
try:
    # uwsgi always = web mode
    import uwsgi
    config.BOOTING = 'web'
except ImportError:
    uwsgi = None
    config.BOOTING = getattr(config, 'BOOTING', False) or sys.argv[1]

# Import app for uwsgi shortcut
from app import app

# The app is wrapped by flask-uwsgi-websocket, and app.run will exit with the uwsgi command
if uwsgi is None and config.BOOTING == 'web':
    app.run(app='boot:app', gevent=config.GEVENT, port=config.PORT)
    sys.exit(0) # just in case ;)


# Now we're booting something, web+uwsgi or task+pytask

# Import shared object maps
from app import module_map, object_map, item_map, task_map, websocket_map # noqa

# Import shared utils
from util.log import logger

# Import shared models
from models import user, permission # noqa

# Import core websockets
from websockets import task # noqa

# Import core tasks
from tasks import update # noqa


# Import all modules & their objects/websockets/tasks
for name in [d for d in listdir('modules') if not path.isfile(path.join('modules', d))]:
    logger.debug('Loading module: {0}'.format(name))

    # Import the module
    module = import_module('modules.{0}'.format(name))
    import_module('modules.{0}.views'.format(name))
    import_module('modules.{0}.config'.format(name))

    module_map[name] = module
    object_map[name] = {}
    item_map[name] = {}
    websocket_map[name] = {}
    task_map[name] = {}

    # Module load?
    if hasattr(module, 'load'):
        logger.debug('[{0}] Module load'.format(name))
        module.load()

    # Get objects
    files = glob(path.join('modules', name, 'models', '*.py'))
    for file in files:
        if file.endswith('__.py'): continue
        file = path.basename(file).replace('.py', '')
        logger.debug('[{0}] Importing models file: {1}'.format(name, file))
        import_module('modules.{0}.models.{1}'.format(name, file))

    # Get websockets
    files = glob(path.join('modules', name, 'websockets', '*.py'))
    for file in files:
        if file.endswith('__.py'): continue
        file = path.basename(file).replace('.py', '')
        logger.debug('[{0}] Importing websocket file: {1}'.format(name, file))
        import_module('modules.{0}.websockets.{1}'.format(name, file))

    # Get tasks
    files = glob(path.join('modules', name, 'tasks', '*.py'))
    for file in files:
        if file.endswith('__.py'): continue
        file = path.basename(file).replace('.py', '')
        logger.debug('[{0}] Importing task file: {1}'.format(name, file))
        import_module('modules.{0}.tasks.{1}'.format(name, file))


# Booting web mode?
if config.BOOTING == 'web':
    from flask import Blueprint

    # Import web utils
    from util.web import route, template, csrf # noqa

    # Import views
    from views import dashboard, account, error, object, objects, websocket # noqa
    from views.admin import debug, logs, permissions, settings, users, dashboard # noqa

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
        app.register_blueprint(module_blueprint)

    # Import web util's pubsub to kickstart listen thread
    from util.web import pubsub # noqa


# Booting task mode?
elif config.BOOTING == 'task':
    from app import task_app

    # Boot pytask
    if __name__ == '__main__':
        pytask_map = {}
        for _, tasks in task_map.iteritems():
            for _, task_class in tasks.iteritems():
                pytask_map[task_class.NAME] = task_class

        task_app.run(pytask_map)
