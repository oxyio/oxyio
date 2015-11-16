# oxy.io
# File: oxyio/scripts/run.py
# Desc: management commands for running the web/task servers


from boot import boot_task

from .. import settings
from ..app import manager, web_app, task_app, task_map


@manager.command
def runserver():
    '''Run the oxy.io webserver.'''
    web_app.run(app='boot:web_app', gevent=settings.GEVENT, port=settings.PORT)


@manager.command
def runworker():
    '''Bootstrap & run the oxy.io task worker.'''
    boot_task()

    pytask_map = {}
    for _, tasks in task_map.iteritems():
        for _, task_class in tasks.iteritems():
            pytask_map[task_class.NAME] = task_class

    task_app.run(pytask_map)
