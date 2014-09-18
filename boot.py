#!/usr/bin/env python

# Oxypanel
# File: boot.py
# Desc: uwsgi & dev entry-point -> imports & bootstrap Oxypanel modules/objects

from os import listdir, path
from importlib import import_module

from flask import Blueprint


# Import config
import config

# Import the app namespace
from app import app, assets, db, module_map, object_map

# Import utils
from util import log, templates, route, csrf

# Import core views
from views import dashboard, account, error, object, objects
from views.admin import debug, logs, permissions, settings, users, dashboard

# Import core models
from models import user, permission


# Imports modules & their objects
def load_modules():
    # Load all modules
    for name in [d for d in listdir('modules') if not path.isfile(path.join('modules', d))]:
        log.debug('Loading module: {0}'.format(name))

        # Import the module
        module = import_module('modules.{0}'.format(name))
        import_module('modules.{0}.views'.format(name))
        import_module('modules.{0}.config'.format(name))

        module_map[name] = module
        object_map[name] = {}

        # Module load?
        if hasattr(module, 'load'):
            log.debug('[{0}] Module load'.format(name))
            module.load()

        # Load objects
        if hasattr(module.config, 'OBJECTS'):
            for file_name, classes in module.config.OBJECTS.iteritems():
                for (db_name, object_class) in classes:
                    log.debug('[{0}] Loading object: {1}'.format(name, object_class))

                    # Import the object
                    object_module = import_module('modules.{0}.models.{1}'.format(name, file_name))
                    object_data = getattr(object_module, object_class)
                    object_map[name][db_name] = object_data


# Bootstrap Oxypanel
# do flask blueprints & routes
def boot():
    load_modules()

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
                log.debug('[{0}] Adding module URL rule: {1} -> {2}'.format(name, url, func))
                module_blueprint.add_url_rule(url, methods=methods, view_func=func)

        # Register blueprint
        app.register_blueprint(module_blueprint)


# uWSGI mode
try:
    import uwsgi
    uwsgi.port_fork_hook = boot
except ImportError:
    pass

# Dev mode
if __name__ == '__main__':
    boot()
    app.run()
