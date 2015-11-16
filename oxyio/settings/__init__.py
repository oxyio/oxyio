# oxy.io
# File: oxyio/settings/__init__.py
# Desc: settings classmodule allowing for defaults + modules applied at runtime

import sys


from . import defaults


class OxyioSettings(object):
    def __init__(self):
        # Apply the defaults to this
        self.apply_attrs(defaults)

    def load_module(self, name):
        # The sys.modules hack below breaks the import
        from importlib import import_module

        settings_module = import_module(name)
        self.apply_attrs(settings_module)

    def apply_attrs(self, module):
        for key in [name for name in dir(module) if name.isupper()]:
            setattr(self, key, getattr(module, key))


sys.modules[__name__] = OxyioSettings()
