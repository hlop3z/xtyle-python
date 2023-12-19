from .core import Tables
from .sample import component as component_samples


class Declaration:
    """Global Typescript Declarations"""

    code: str


class Props:
    """Global Reusable Props Declarations"""

    code: str


class Style:
    """SCSS Style Sheet"""

    code: str


class Sample:
    """Global Sample Codes"""

    code: str
    language: str
    label: str


class JinjaTemplate:
    code: str
    args: dict


class Module:
    """Javascript/Typescript Module (Plugin)"""

    base_id: int
    build_id: str
    is_global: bool
    merge: bool
    docs: str

    actions: str
    directives: str
    globals: str
    init: str
    models: str
    router: str
    store: str

    # install: str


class Base:
    """HTML Template Base"""

    path: str
    code: str
    docs: str


class Cache:
    """Global Cached Modules"""

    module: dict
    views: dict
    plugins: dict
    declarations: str
    build_id: int


class Store:
    """Global Data Objects"""

    data: dict


class Component:
    """Frontend Component"""

    code: str
    style: str
    props: str
    docs: str
    preview: str


class View:
    """Frontend View"""

    path: str
    code: str
    style: str
    # docs: str
    base_id: int
    preview: str


class Plugin:
    """Frontend Javascript/Typescript Plugins"""

    # package: dict
    version: str
    style: str
    javascript: str
    declarations: str


schema = Tables(
    base=Base,
    cache=Cache,
    component=Component,
    declaration=Declaration,
    module=Module,
    plugin=Plugin,
    sample=Sample,
    store=Store,
    view=View,
    jinja=JinjaTemplate,
    props=Props,
    style=Style,
)


SAMPLE_CODE_LANGUAGES = {
    "base": "html",
    "code": "javascript",
    "style": "scss",
    "docs": "javascript",
    "props": "typescript",
    # "preview": "javascript",
    # "directives": "javascript",
    # "globals": "javascript",
    # "router": "javascript",
    # "store": "javascript",
    # "init": "javascript",
}

SAMPLE_CODE_LABEL = {
    "base": "app/bases",
    "code": "components/views",
    "style": "components/views",
    "docs": "components",
    "props": "components",
    # "preview": "components/views",
    # "directives": "projects/modules",
    # "globals": "projects/modules",
    # "router": "projects/modules",
    # "store": "projects/modules",
    # "init": "projects/modules",
}
SAMPLE_CODE_DEFAULT = {
    key.split("_")[0].strip(): value.text
    for key, value in component_samples._asdict().items()
}


COMPONENT_SAMPLE_NAMES = ["code", "style", "docs", "props", "preview"]
# MODULE_SAMPLE = ["directives", "globals", "init", "router", "store"]
