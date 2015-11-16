# Oxypanel
# File: scripts/database.py
# Desc: perform/manage database migrations

from os import path

from flask.ext.script import Manager
from flask.ext.migrate import (
    init as flask_init,
    migrate as flask_migrate,
    upgrade as flask_upgrade,
    show as flask_show
)

from ..app import manager


def _module_directory(name):
    if name == 'core':
        return 'migrations'

    return path.join('modules', name, 'migrations')


db_manager = Manager(usage='Manage database migrations')

@db_manager.command
def init(name):
    flask_init(directory=_module_directory(name))

@db_manager.command
def migrate(name):
    flask_migrate(directory=_module_directory(name))

@db_manager.command
def upgrade(name):
    flask_upgrade(directory=_module_directory(name))

@db_manager.command
def show(name):
    flask_show(directory=_module_directory(name))


manager.add_command('db', db_manager)
