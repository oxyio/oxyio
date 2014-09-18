# Oxypanel
# File: app/__init__.py
# Desc: the globals file (app, connections, maps)

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_debugtoolbar import DebugToolbarExtension
from webassets import Environment
from pylibmc import Client as MemcacheClient

import config

# App
app = Flask('oxypanel')
app.debug = config.DEBUG
app.secret_key = config.SECRET

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
migrate = Migrate(app, db)

# Manager/scripts
manager = Manager(app, with_default_commands=False)
manager.add_command('db', MigrateCommand)

# Cache
cache = MemcacheClient(config.CACHE_HOSTS, binary=True)

# Assets
assets = Environment('', '')
assets.debug = config.DEBUG

# Maps module names => {views, models, config}
module_map = {}

# Maps object <module>-<name>s => object class
object_map = {}

# Debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)
