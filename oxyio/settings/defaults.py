# oxy.io
# File: oxyio/settings/defaults.py
# Desc: default settings for oxy.io

# Expected to be provided
# SECRET
# SSH_KEY_PRIVATE
# SSH_KEY_PUBLIC
# DATABASE_NAME
# DATABASE_USER
# DATABASE_PASSWORD

DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = 3306

ES_NODES = [
    ('127.0.0.1', 9200)
]

REDIS_NODES = [
    ('127.0.0.1', 6379)
]

DEBUG = False
NAME = 'Oxygem'

BCRYPT_ROUNDS = 12

PORT = 5000
GEVENT = 100

DATABASE_DRIVER = 'mysql+mysqldb'

ES_LOG_INDEX = 'oxypanel_logs'
ES_DATA_INDEX = 'oxypanel_data'

REDIS_TASK_SET = 'tasks'
REDIS_TASK_PREFIX = 'task-'
REDIS_NEW_QUEUE = 'new-task'
REDIS_END_QUEUE = 'end-task'
REDIS_ERROR_QUEUE = 'error-task'
REDIS_WEBSOCKET_PREFIX = 'websocket-request-'

SSH_TIMEOUT = 5
SSH_RETRIES = 3
SSH_KEY_PASSWORD = None
