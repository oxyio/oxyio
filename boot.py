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
    import uwsgi
    config.BOOTING = 'web'
except ImportError:
    uwsgi = None
    config.BOOTING = sys.argv[1]

# Import the shared app namespace
from app import app, module_map, object_map

# The app is wrapped by flask-uwsgi-websocket, and app.run will exit with the uwsgi command
if uwsgi is None and config.BOOTING == 'web':
    app.run(app='boot:app', gevent=100, port=config.PORTS['WEB'])
    sys.exit(0)
# Now we're booting something, web+uwsgi or task+pytask

# Import shared utils
from util.log import logger

# Import shared models
from models import user, permission # noqa

# Imports modules & their objects
# importable (manage.py)
def load_modules():
    # Load all modules
    for name in [d for d in listdir('modules') if not path.isfile(path.join('modules', d))]:
        logger.debug('Loading module: {0}'.format(name))

        # Import the module
        module = import_module('modules.{0}'.format(name))
        import_module('modules.{0}.views'.format(name))
        import_module('modules.{0}.config'.format(name))

        module_map[name] = module
        object_map[name] = {}

        # Module load?
        if hasattr(module, 'load'):
            logger.debug('[{0}] Module load'.format(name))
            module.load()

        # Load objects
        if hasattr(module.config, 'OBJECTS'):
            for file_name, classes in module.config.OBJECTS.iteritems():
                for (db_name, object_class) in classes:
                    logger.debug('[{0}] Loading object: {1}'.format(name, object_class))

                    # Import the object
                    object_module = import_module('modules.{0}.models.{1}'.format(name, file_name))
                    object_data = getattr(object_module, object_class)
                    object_map[name][db_name] = object_data
load_modules()


# Booting web mode?
if config.BOOTING == 'web':
    from flask import Blueprint

    # Import web utils
    from util.web import route, template, csrf # noqa

    # Import core views
    from views import dashboard, account, error, object, objects # noqa
    from views.admin import debug, logs, permissions, settings, users, dashboard # noqa

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


# Booting task mode?
elif config.BOOTING == 'task':
    from app import task_app

    # Import core tasks
    from tasks import task, update # noqa

    # Load the tasks from each module
    for module_name in module_map.keys():
        files = glob(path.join('modules', module_name, 'tasks', '*.py'))

        for file in files:
            if file.endswith('__.py'): continue
            file = path.basename(file).replace('.py', '')
            logger.debug('[{0}] Adding task: {1}'.format(module_name, file))
            import_module('modules.{0}.tasks.{1}'.format(module_name, file))

    # Boot pytask
    if __name__ == '__main__':
        task_app.run()
