# Oxypanel
# File: app.py
# Desc: the globals file (app, connections, maps)
#       shared by: web | task | websocket

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis

import config
# We shouldn't really import anything Oxypanel related in this file to avoid
# circular imports everything imports from app, except the base meta, which is
# required for creating the SQLAlchemy instance
from models.meta import BaseMeta


# App
# a Flask instance represents "app" for web, tasks & websockets
app = Flask('oxypanel')
app.debug = config.DEBUG
app.secret_key = config.SECRET

# Redis
host, port = config.REDIS['HOSTS'][0].split(':')
redis_client = StrictRedis(host, port=port)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = '{0}://{1}:{2}@{3}:{4}/{5}'.format(
    config.DATABASE['DRIVER'],
    config.DATABASE['USER'],
    config.DATABASE['PASSWORD'],
    config.DATABASE['HOST'],
    config.DATABASE['PORT'],
    config.DATABASE['NAME']
)
db = SQLAlchemy(app, base_metaclass=BaseMeta)

# Map core names -> classes
module_map = {}
object_map = {}
item_map = {}
# There are only core websockets & tasks
websocket_map = {
    'core': {}
}
task_map = {
    'core': {}
}

# Webserver
if config.BOOTING == 'web':
    from webassets import Environment
    from flask_debugtoolbar import DebugToolbarExtension
    from flask.ext.uwsgi_websocket import GeventWebSocket

    # Debug toolbar
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    toolbar = DebugToolbarExtension(app)

    # Assets
    assets = Environment('', '')
    assets.debug = config.DEBUG

    # Websockets
    websocket = GeventWebSocket(app, timeout=30) # setting any timeout seems to = infinite (def = 60s)


# Tasks
elif config.BOOTING == 'task':
    from pytask import PyTask, Monitor

    # pytask
    task_app = PyTask(
        redis_client,
        new_queue=config.REDIS['NEW_QUEUE'],
        end_queue=config.REDIS['END_QUEUE'],
        task_prefix=config.REDIS['TASK_PREFIX']
    )

    # Add & prep monitor task
    task_app.add_task(Monitor)
    task_app.pre_start_task('pytask/monitor')


# Manager
elif config.BOOTING == 'manage':
    from flask.ext.script import Manager
    from flask.ext.migrate import Migrate, MigrateCommand

    # Manager/scripts
    manager = Manager(app, with_default_commands=False)

    # Migrate system init
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
