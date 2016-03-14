# oxy.io
# File: app/module_loader.py
# Desc: loads oxy.io modules

from glob import glob
from os import path
from importlib import import_module

from oxyio import settings
from oxyio.log import logger

from . import module_map


def has_module(name):
    '''
    Checks if a module is present.
    '''

    return name in settings.MODULES


def _load_module_files(name, folder):
    files = glob(path.join(settings.ROOT, name, folder, '*.py'))

    for filename in files:
        # Skip __init__.py
        if filename.endswith('__.py'):
            continue

        # Load/import the file
        filename = path.basename(filename).replace('.py', '')
        logger.debug('[{0}] Importing {1} file: {2}'.format(name, folder, filename))
        import_module('oxyio.{0}.{1}.{2}'.format(name, folder, filename))


def load_module(name):
    '''
    Load a module.
    '''

    logger.debug('Loading module: {0}'.format(name))

    # Import the module
    module = import_module('oxyio.{0}'.format(name))
    import_module('oxyio.{0}.config'.format(name))

    # Attach to the global module namespace
    module_map[name] = module

    # Module load?
    if hasattr(module, 'load'):
        logger.debug('[{0}] Module load'.format(name))
        module.load()

    # Load module models/objects, websockets & tasks
    _load_module_files(name, 'models')
    _load_module_files(name, 'websockets')
    _load_module_files(name, 'tasks')
