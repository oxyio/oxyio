#!/usr/bin/env python

# Oxypanel
# File: manage.py
# Desc: management commands!
#       this file does not, by default, load all the modules/etc
#       this is to prevent log messages appearing at the start for things like node_config

import os
import sys

from flask.ext.script import Shell

import config
config.BOOTING = 'manage'

from app import manager
from scripts import user, node # noqa


if __name__ == '__main__':
    # Force unbuffered python
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    # Shell
    if 'shell' in sys.argv:
        from boot import load_modules
        load_modules()
        manager.add_command('shell', Shell())

    # Db
    if 'db' in sys.argv:
        from boot import load_modules
        load_modules()

    # Run manager
    manager.run()
