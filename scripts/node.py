# Oxypanel
# File: scripts/node.py
# Desc: autogenerated node config (as JSON) based on dynamic config.py

import json

import config
from app import manager


@manager.command
def node_config():
    print json.dumps({
        'debug': config.DEBUG,
        'es_nodes': config.ES_NODES,
        'ssh_key': {
            'private': config.SSH_KEY[0],
            'public': config.SSH_KEY[1],
            'pass': config.SSH_KEY_PASS
        }
    })
