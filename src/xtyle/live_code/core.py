from collections import namedtuple
from types import SimpleNamespace

MODULE_NAME = "xtyle"

PLUGIN_UNIQUE_NAME = "xtyle_theme_bundle_global_name"

VIEW_KEY = SimpleNamespace(one="INSTALLED_VIEWS", all="INSTALLED_VIEWS")

THEME_MODELS = ["component", "view", "plugin", "style"]

ENVIRONMENT_MODELS = [
    "module",
    "base",
    "plugin",
    "declaration",
    "store",
    "cache",
    "sample",
    "jinja",
    "props",
    "style",
]

ALL_UNIQUE_MODELS = list(set(THEME_MODELS + ENVIRONMENT_MODELS))

PLUGIN_FIELDS = [
    "javascript",
    "style",
    "declarations",
]


Theme = namedtuple(
    "Module",
    THEME_MODELS,
    module=MODULE_NAME,
)

Environment = namedtuple(
    "Environment",
    ENVIRONMENT_MODELS,
    module=MODULE_NAME,
)


StaticPlugin = namedtuple(
    "StaticPlugin",
    PLUGIN_FIELDS,
    module=MODULE_NAME,
)

Tables = namedtuple(
    "Tables",
    ALL_UNIQUE_MODELS,
    module=MODULE_NAME,
)
