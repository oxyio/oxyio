#!/usr/bin/env python

# oxy.io
# File: manage.py
# Desc: bootstrap oxy.io and execute the manager

import os
import sys

from flask.ext.script import Shell

import boot # noqa

from oxyio.app import manager
from oxyio.scripts import user, database # noqa


if __name__ == '__main__':
    # Force unbuffered python
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    # Add the shell command
    manager.add_command('shell', Shell())

    # Run the manager!
    manager.run()
