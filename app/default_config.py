# Oxypanel
# File: config.py
# Desc: settings for oxypanel

# Expected to be provided in config.py
# SECRET
# SSH_KEY_PRIVATE
# SSH_KEY_PUBLIC
# DATABASE_DRIVER
# DATABASE_NAME
# DATABASE_HOST
# DATABASE_PORT
# DATABASE_USER
# DATABASE_PASSWORD
# ES_NODES
# REDIS_NODES

DEBUG = False
NAME = 'Oxygem'

BCRYPT_ROUNDS = 12

PORT = 5000
GEVENT = 100

ES_LOG_INDEX = 'oxypanel_logs'
ES_DATA_INDEX = 'oxypanel_data'

REDIS_TASK_SET = 'tasks'
REDIS_TASK_PREFIX = 'task-'
REDIS_NEW_QUEUE = 'new-task'
REDIS_END_QUEUE = 'end-task'
REDIS_ERROR_QUEUE = 'error-task'
REDIS_WEBSOCKET_PREFIX = 'websocket-request-'

SSH_TIMEOUT = 5
SSH_RETRIES = 0
SSH_KEY_PASSWORD = None
