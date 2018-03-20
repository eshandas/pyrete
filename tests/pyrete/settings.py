import os
import importlib

settings = importlib.import_module(os.environ['PYRETE_SETTINGS_MODULE'])
