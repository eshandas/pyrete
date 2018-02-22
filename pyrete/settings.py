import os
import importlib


settings = importlib.import_module(os.environ.data['PYRETE_SETTINGS_MODULE'])
