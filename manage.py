#!/usr/bin/env python

# oxy.io
# File: manage.py
# Desc: bootstrap oxy.io and execute the manager

from flask.ext.script import Shell


if __name__ == '__main__':
    import os
    import sys

    # Force unbuffered python
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    # Bootstrap oxy.io
    import boot # noqa

    # Import the management scripts
    from oxyio.scripts import run, user, database # noqa

    # Import the manager
    from oxyio.app import manager

    # Add the shell command
    manager.add_command('shell', Shell())

    # Run the manager!
    manager.run()
