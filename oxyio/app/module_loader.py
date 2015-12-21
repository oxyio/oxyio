# oxy.io
# File: app/module_loader.py
# Desc: loads oxy.io modules

from glob import glob
from os import listdir, path
from importlib import import_module

from oxyio.util.log import logger

from . import module_map, object_map, item_map, websocket_map, task_map


def list_modules():
    '''Lists modules from ./modules/.'''

    return [
        d for d in listdir('modules')
        if path.isdir(path.join('modules', d))
    ]


def load_module(name):
    '''Load a module.'''

    logger.debug('Loading module: {0}'.format(name))

    # Import the module
    module = import_module('modules.{0}'.format(name))
    import_module('modules.{0}.config'.format(name))
    import_module('modules.{0}.web.views'.format(name))

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
