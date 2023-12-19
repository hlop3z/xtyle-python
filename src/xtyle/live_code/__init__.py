# from .sample import sample
from .types import schema, Tables
from .core import ENVIRONMENT_MODELS
from .plugin_gzip import PluginGzip as gzip
from .environment import XtyleEnvironment as Environment


environment_models = list(filter(lambda x: x not in ["plugin"], ENVIRONMENT_MODELS))
