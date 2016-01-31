# oxy.io
# File: oxyio/app/__init__.py
# Desc: the globals file (app, connections, maps)

from os import path

from flask import Flask
from pytask import PyTask
from redis import StrictRedis
from flask.ext.script import Manager
from flask.ext.uwsgi_websocket import GeventWebSocket
from elasticsearch import Elasticsearch, RequestsHttpConnection

from oxyio import settings

from .custom_sqlalchemy import SQLAlchemy


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
web_app = Flask('oxyio',
    static_folder=path.join(settings.ROOT, 'web', 'static'),
    template_folder=path.join(settings.ROOT, 'web', 'templates')
)
web_app.debug = settings.DEBUG
web_app.secret_key = settings.SECRET
# Ensures request_teardown functions are called even in debug
web_app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

# Websocket server
websocket_app = GeventWebSocket(web_app, timeout=settings.WEBSOCKET_TIMEOUT)

# Manager/scripts
manager = Manager(web_app, with_default_commands=False)

# Redis
# TODO: use redis-py-cluster
redis_client = StrictRedis(*settings.REDIS_NODES[0])

# Elasticsearch
es_client = Elasticsearch(
    ['{0}:{1}'.format(*node) for node in settings.ES_NODES],
    connection_class=RequestsHttpConnection, sniff_on_start=False
)

# Database
web_app.config['SQLALCHEMY_DATABASE_URI'] = '{0}://{1}:{2}@{3}:{4}/{5}'.format(
    settings.DATABASE_DRIVER,
    settings.DATABASE_USER,
    settings.DATABASE_PASSWORD,
    settings.DATABASE_HOST,
    settings.DATABASE_PORT,
    settings.DATABASE_NAME
)
db = SQLAlchemy(web_app)

# Task worker
task_app = PyTask(
    redis_client,
    new_queue=settings.REDIS_NEW_QUEUE,
    end_queue=settings.REDIS_END_QUEUE,
    task_prefix=settings.REDIS_TASK_PREFIX
)
