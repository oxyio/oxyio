# oxy.io
# File: app/module_loader.py
# Desc: loads oxy.io modules

from glob import glob
from os import listdir, path
from importlib import import_module

from oxyio.util.log import logger

from . import module_map, object_map, item_map, websocket_map, task_map


MODULE_NAMES = None

def list_modules():
    '''Lists modules from ./modules/.'''

    global MODULE_NAMES

    if MODULE_NAMES is None:
        MODULE_NAMES = [
            d for d in listdir('modules')
            if path.isdir(path.join('modules', d))
        ]

    return MODULE_NAMES


def has_module(name):
    '''Checks if a module is present.'''

    return name in list_modules()


def _load_module_files(name, folder):
    files = glob(path.join('modules', name, folder, '*.py'))

    for filename in files:
        # Skip __init__.py
        if filename.endswith('__.py'):
            continue

        # Load/import the file
        filename = path.basename(filename).replace('.py', '')
        logger.debug('[{0}] Importing {1} file: {2}'.format(name, folder, filename))
        import_module('modules.{0}.{1}.{2}'.format(name, folder, filename))


def load_module(name):
    '''Load a module.'''

    logger.debug('Loading module: {0}'.format(name))

    # Import the module
    module = import_module('modules.{0}'.format(name))
    import_module('modules.{0}.config'.format(name))
    import_module('modules.{0}.web.views'.format(name))

    # Setup the global namespace
    module_map[name] = module
    object_map[name] = {}
    item_map[name] = {}
    websocket_map[name] = {}
    task_map[name] = {}

    # Module load?
    if hasattr(module, 'load'):
        logger.debug('[{0}] Module load'.format(name))
        module.load()

    # Load module models/objects, websockets & tasks
    _load_module_files(name, 'models')
    _load_module_files(name, 'websockets')
    _load_module_files(name, 'tasks')
