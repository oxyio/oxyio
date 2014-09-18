#!/usr/bin/env python

# Oxypanel
# File: manage.py
# Desc: management commands!

import os
import sys

from flask.ext.script import Shell

from app import manager
from scripts import user, node # noqa


if __name__ == '__main__':
    # Force unbuffered python
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    # Run shell
    if 'shell' in sys.argv:
        from boot import load_modules
        load_modules()
        manager.add_command('shell', Shell())

    # Run manager
    manager.run()
