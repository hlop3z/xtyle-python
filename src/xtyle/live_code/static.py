import json
import pathlib
from types import SimpleNamespace
import functools

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

try:
    from django.templatetags.static import static
    from django.urls import reverse

    django_available = True
except ImportError:
    django_available = False


def static_script(static, url):
    return f"""<script src="{static(url)}" type="text/javascript"></script>"""


def static_style(static, url):
    return f"""<link href="{static(url)}" rel="stylesheet">"""


def load_config(base_dir: pathlib.Path) -> SimpleNamespace:
    xtyle_file = "xtyle.config.json"
    config_json = None
    try:
        with open(base_dir / xtyle_file, "r") as f:
            config_json = SimpleNamespace(**json.load(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file '{xtyle_file}' not found.")
    except json.JSONDecodeError:
        raise ValueError("Error decoding JSON. Check the format of the config file.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")
    return config_json


def clean_value(value):
    if value == "":
        return None
    return value


class XtyleApp:
    def __init__(
        self,
        base_dir: str = None,
        root: str = None,
        base_url: str = None,
        rename: dict = None,
        templates_dir: pathlib.Path | str = None,
        static_method=None,
        reverse_method=None,
    ):
        # Core Variables
        self._root = root
        self._base_url = base_url

        # Core Path(s)
        self.base_dir = base_dir
        self.templates_dir = templates_dir or base_dir / "templates"
        self.html_file = "xtyle.html"

        # INIT Path(s)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Load Config
        self.config = load_config(self.base_dir)
        self._create_base_file()

        rename = rename or {}
        self._rename = {rename.get(k, k): k for k in self.config.keys}
        self._rename_reverse = {k: rename.get(k, k) for k in self.config.keys}

        # Check for Django dependencies
        if django_available:
            static_func = static_method or static
            reverse_func = reverse_method or reverse
        else:
            static_func = static_method
            reverse_func = reverse_method

        # JINJA
        self.static_method = static_func
        self.reverse_method = reverse_func
        self._init_jinja(
            static=static_func,
            reverse=reverse_func,
        )

    def load_config(self):
        self.config = load_config(self.base_dir)

    def render(self, __url_path__, **kwargs):
        input_name = self.get_app_from_url(__url_path__)
        app_name = self._rename.get(input_name)
        method = self._apps.get(app_name)
        if method:
            return method(**kwargs)
        else:
            method = self._apps.get(self._root)
            if method:
                return method(**kwargs)
        return "<h1>Page Not Found!<h1>"

    def get_app_from_url(self, url_string):
        url_parts = [clean_value(part) for part in (url_string or "").split("/")]
        root_name = url_parts[0] or self._root
        if self._base_url and self._base_url == root_name and len(url_parts) > 1:
            root_name = url_parts[1]
        return root_name

    @staticmethod
    def json_jinja(data):
        return Markup(json.dumps(data))

    @staticmethod
    def json_const(name: str, data: dict):
        return Markup(f"\nconst {name} = {json.dumps(data)}")

    @staticmethod
    def base_html_string(string_template: str):
        return "{% extends 'base.html' %}" + (string_template or " ")

    def static_script(self, path):
        return static_script(self.static_method, path)

    def static_style(self, path):
        return static_style(self.static_method, path)

    def _create_base_file(self):
        with open(self.templates_dir / self.html_file, "w") as f:
            f.write(self.config.base)

    def blank_template(self, **kwargs):
        return self.env.from_string(self.base_html_string(None)).render(**kwargs)

    def core_template(self, __string_template__, **kwargs):
        return self.env.from_string(self.base_html_string(__string_template__)).render(
            **kwargs
        )

    def _start_templates(self):
        template = lambda code: functools.partial(self.core_template, code)
        with_jinja_render = {}
        for (
            name,
            code,
        ) in self.config.templates.items():
            with_jinja_render[name] = template(code)
        return with_jinja_render

    def _init_jinja(
        self,
        static=None,
        reverse=None,
    ):
        # (JINJA) Environment
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True,
            auto_reload=False,
            # cache_size=50,
        )

        # Environment Tools
        self.env.globals.update(
            {
                "static": static,
                "url": reverse,
                "json": self.json_jinja,
                "const": self.json_const,
            }
        )

        # Apps Templates
        self._templates = self._start_templates()
        self._apps = self._start_apps()

    def _start_apps(self):
        with_jinja_render = {}
        base_apps = f"{self.config.path}/apps"
        for name, template_name in self.config.apps.items():
            template = self._templates.get(template_name)

            # Static
            the_scripts = []
            if self.config.global_script:
                the_scripts.append(self.static_style(f"{self.config.path}/style.css"))
            if self.config.global_style:
                the_scripts.append(self.static_script(f"{self.config.path}/index.js"))

            # Current App
            the_scripts.append(self.static_script(f"{base_apps}/{name}.js"))
            final_script = "\n".join(the_scripts)
            xtyle_use = (
                f"""\n<script type="text/javascript">xtyle.use({name})</script>"""
            )
            base_url = self._rename_reverse.get(name) if self._root != name else ""
            root_base_url = self._base_url + "/" if self._base_url else ""
            xtyle_router = {
                "baseURL": f"{root_base_url}{base_url}/".replace("//", "/"),
                "history": True,
            }
            xtyle_init = Markup(
                f"""<script type="text/javascript"> xtyle.init(() => h(xtyle.router.views), document.body, {json.dumps(xtyle_router)})</script>"""
            )

            # Template
            if template:
                with_jinja_render[name] = functools.partial(
                    template,
                    xtyle=Markup(final_script + xtyle_use),
                    init=xtyle_init,
                )
            else:
                with_jinja_render[name] = functools.partial(
                    self.blank_template,
                    xtyle=Markup(final_script + xtyle_use),
                    init=xtyle_init,
                )

        return with_jinja_render
