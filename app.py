# Oxypanel
# File: app.py
# Desc: the globals file (app, connections, maps)
#       shared by: web | task | websocket

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from pylibmc import Client as MemcacheClient
from redis import StrictRedis

import config


# App
# a Flask instance represents "app" for web, tasks & websockets
app = Flask('oxypanel')
app.debug = config.DEBUG
app.secret_key = config.SECRET

# (mem)Cache
cache = MemcacheClient(config.CACHE_HOSTS, binary=True)

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
db = SQLAlchemy(app)

# Maps module names => {views, models, config}
module_map = {}

# Maps object <module>-<name>s => object class
object_map = {}


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

    ws = GeventWebSocket(app)


# Tasks
elif config.BOOTING == 'task':
    from pytask import PyTask

    # pytask
    task_app = PyTask(
        redis_client,
        new_queue=config.REDIS['NEW_QUEUE'],
        end_queue=config.REDIS['END_QUEUE'],
        task_prefix=config.REDIS['TASK_PREFIX']
    )


# Manager
elif config.BOOTING == 'manage':
    from flask.ext.script import Manager
    from flask.ext.migrate import Migrate, MigrateCommand

    # Manager/scripts
    manager = Manager(app, with_default_commands=False)

    # Migrate system init
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
