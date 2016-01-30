# oxy.io
# File: oxyio/tasks/base.py
# Desc: wrapper around PyTask.Task with metaclass to transparently add to global map

from pytask import Task as PyTask

from oxyio.app import task_map
from oxyio.log import logger


class MetaTask(type):
    '''Metaclass that attaches Task classes to task_map.'''

    def __init__(cls, name, bases, d):
        if name != 'Task':
            module_name, task_name = cls.NAME.split('/')
            task_map[module_name][task_name] = cls

            logger.debug('Registered task {0}/{1}'.format(
                module_name, task_name
            ))

        super(MetaTask, cls).__init__(name, bases, d)


class Task(PyTask):
    __metaclass__ = MetaTask
