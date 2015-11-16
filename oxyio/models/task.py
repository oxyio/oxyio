# Oxypanel
# File: models/task.py
# Desc: base task with metaclass to transparently add to global map

from pytask import Task as PyTask

from ..app import task_map


class MetaTask(type):
    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)
        if name != 'Task':
            module_name, task_name = cls.NAME.split('/')
            task_map[module_name][task_name] = cls

class Task(PyTask):
    __metaclass__ = MetaTask
