import json

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

try:
    from django.templatetags.static import static
    from django.urls import reverse

    django_available = True
except ImportError:
    django_available = False


class Template:
    def __init__(
        self,
        templates_dir,
        static_method=None,
        reverse_method=None,
    ):
        # Check for Django dependencies
        if django_available:
            static_func = static_method or static
            reverse_func = reverse_method or reverse
        else:
            static_func = static_method
            reverse_func = reverse_method

        # Environment
        self.env = Environment(loader=FileSystemLoader(templates_dir))

        # Update global variables
        self.env.globals.update(
            {
                "static": static_func,
                "url": reverse_func,
                "json": lambda data: Markup(json.dumps(data)),
                "const": self.json_const,
                "csrf_token": "csrf_token",
            }
        )

    def render(self, template_path, **kwargs):
        # Load the template from the file
        template = self.env.get_template(template_path)

        # Render the template with variables
        return template.render(**kwargs)

    def string(self, template_string, **kwargs):
        # Load the template from the string
        template = self.env.from_string(template_string)

        # Render the template with variables
        return template.render(**kwargs)

    def globals(self, **kwargs):
        self.env.globals.update(kwargs)

    @staticmethod
    def json_const(name: str, data: dict):
        return Markup(f"\nconst {name} = {json.dumps(data)}")
