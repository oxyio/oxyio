# oxy.io
# File: oxyio/scripts/database.py
# Desc: perform/manage database migrations

from os import path

from alembic import command
from alembic.config import Config
from flask.ext.script import Manager

from boot import boot_all_modules
from oxyio.app import manager


def _get_module_config(module_name):
    # Version table is always module_version
    versions_table = '{0}_version'.format(module_name)

    # If module is actually oxy.io core
    if module_name == 'core':
        versions_dir = path.join('oxyio', 'migrations')

    # Otherwise load the module
    else:
        versions_dir = path.join('modules', module_name, 'migrations')

    boot_all_modules()

    config = Config(path.join('alembic', 'alembic.ini'))
    config.set_main_option('script_location', 'alembic')
    config.set_main_option('version_locations', versions_dir)

    config.set_section_option('oxyio', 'versions_table', versions_table)
    config.set_section_option('oxyio', 'module_name', module_name)

    return config


db_manager = Manager(usage='Manage database migrations')


@db_manager.command
def migrate(module_name):
    config = _get_module_config(module_name)
    command.revision(config, autogenerate=True)


@db_manager.command
def upgrade(module_name):
    config = _get_module_config(module_name)
    command.upgrade(config, 'head')


manager.add_command('db', db_manager)
