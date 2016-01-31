# oxy.io
# File: oxyio/settings/defaults.py
# Desc: default settings for oxy.io


# Expected to be provided
SECRET = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''

MODULES = tuple()


# "Production" defaults
DEBUG = False

DATABASE_DRIVER = 'mysql+mysqldb'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = 3306

NAME = 'oxy.io'

BCRYPT_ROUNDS = 12

PORT = 5000
GEVENT = 100

WEBSOCKET_TIMEOUT = 30

ES_NODES = [
    ('127.0.0.1', 9200)
]

ES_LOG_INDEX = 'oxyio_logs'
ES_STATS_INDEX = 'oxyio_stats'

ES_INDEX_BATCH = 5000

REDIS_NODES = [
    ('127.0.0.1', 6379)
]

REDIS_TASK_SET = 'tasks'
REDIS_TASK_PREFIX = 'task-'
REDIS_NEW_QUEUE = 'new-task'
REDIS_END_QUEUE = 'end-task'
REDIS_ERROR_QUEUE = 'error-task'

REDIS_WEBSOCKET_PREFIX = 'websocket-request-'
REDIS_INDEX_QUEUE = 'index-stat'
