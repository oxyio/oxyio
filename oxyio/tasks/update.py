# oxy.io
# File: oxyio/tasks/update.py
# Desc: the task that updates oxy.io

from .base import Task


# Update Oxypanel
class Update(Task):
    NAME = 'core/update'

    def __init__(self):
        pass
