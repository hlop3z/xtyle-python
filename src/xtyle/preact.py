"""
Module: Preact
"""

# Python
import functools
import json
import pathlib
import types
import uuid
import os
import shutil

# Extras
import sass
from css_html_js_minify import js_minify
from py_mini_racer import MiniRacer

from .database import DatabaseManager
from .unzip import unzip_component

BASE_DIR = pathlib.Path(__file__).parent

JSX_PARTS = ["docs", "index", "props", "style"]


def initialize() -> functools.partial:
    """
    Initialize the MiniRacer compiler for JSX transformation.

    Returns:
        functools.partial: A callable for JSX transformation.
    """
    ctx = MiniRacer()

    # Files
    babel_path = BASE_DIR / "babel.min.js"
    prettier_path = BASE_DIR / "prettier.min.js"

    # Babel
    with open(babel_path, "r", encoding="utf-8") as b_file:
        babel_code = b_file.read()

    # Prettier
    with open(prettier_path, "r", encoding="utf-8") as p_file:
        prettier_code = p_file.read()

    # Execute (babel.min.js & prettier.min.js)
    ctx.eval(babel_code)
    ctx.eval(prettier_code)

    return functools.partial(ctx.call, "JSX")


class JSX:
    """
    Class providing utilities for working with Preact components and managing their files and data.
    """

    package_name: str = "GUI"
    compile = initialize()
    base_dir: pathlib.Path
    response = types.SimpleNamespace
    debug = False

    @staticmethod
    def scss(code):
        """Database"""
        try:
            return sass.compile(string=code, output_style="compressed")
        except:
            return code or ""

    @classmethod
    def init(
        cls,
        base: pathlib.Path,
        debug: bool = False,
        static: pathlib.Path | None = None,
        templates: pathlib.Path | None = None,
    ) -> str:
        """INIT Class"""
        cls.base_dir = base
        cls.static_dir = static or (base / "static")
        cls.template_dir = templates or (base / "templates" / "components")
        cls.db = DatabaseManager(base / "gui.sqlite3")
        cls.debug = debug

        # INIT Folders
        cls.static_dir.mkdir(parents=True, exist_ok=True)
        cls.template_dir.mkdir(parents=True, exist_ok=True)
        (cls.static_dir / "app").mkdir(parents=True, exist_ok=True)

    @classmethod
    def components(cls, *components) -> str:
        if cls.debug:
            for path in components:
                cls.component(path)
        return ""

    @classmethod
    def component(cls, path: str) -> str:
        """JSX Component"""

        # Name
        kebab_name = path.replace("/", "-").lower()

        # HTML
        element = cls.collect_files(path)
        element.code_component = cls.js_function(cls.compile(element.component))
        element.code_style = cls.scss(element.style or "")

        # Set To Database
        cls.db.set(kebab_name, **element.__dict__)

        # Return Nothing
        return ""

    @classmethod
    def js_function_base(cls, code: str) -> str:
        """JS Base"""
        return "(function () {" + code + "})();"

    @classmethod
    def js_function(cls, code: str) -> str:
        """JS Function"""
        return cls.js_function_base(code.replace("export default", "return"))

    @classmethod
    def live_script(cls, code: str) -> str:
        """JS Live"""
        return f"""<script>{ cls.global_var(code) }</script>"""

    @classmethod
    def global_var(cls, code: str) -> str:
        """
        Wrap the provided JavaScript code in a global variable declaration.

        Args:
            code (str): The JavaScript code to wrap.

        Returns:
            str: JavaScript code wrapped in a global variable declaration.
        """
        return f"var {cls.package_name} = {{}};" + "\n" + code

    @classmethod
    def string(cls, code: str) -> str:
        """
        Transform the provided JSX code using the initialized JSX compiler.

        Args:
            code (str): The JSX code to transform.

        Returns:
            str: Transformed JavaScript code.
        """
        return cls.compile(code)

    # ... (Other methods)

    @classmethod
    def collect_files(cls, folder_name: str) -> types.SimpleNamespace:
        """
        Collect files for a Preact component, compile JSX, and manage data.

        Args:
            folder_name (str): The name of the component folder.

        Returns:
            types.SimpleNamespace: An object containing collected file contents and compiled data.
        """
        component_dir = cls.template_dir / folder_name
        file_contents = {}

        for file_path in component_dir.iterdir():
            if file_path.is_file():
                file_name = file_path.stem
                if file_name in JSX_PARTS:
                    with open(file_path, mode="r", encoding="utf-8") as file:
                        file_contents[file_name] = file.read()

        # Clean
        file_contents["component"] = file_contents["index"]
        del file_contents["index"]

        # HTML <Element />
        return cls.response(**file_contents)

    @classmethod
    def dev(cls) -> str:
        """
        Build Preact components.

        Returns:
            str: Transformed JavaScript code.
        """
        if not cls.debug:
            config = cls.get_config()
            code = f"""<link rel="stylesheet" href="/static/app/{config.css}">""" + "\n"
            code += f"""<script src="/static/app/{config.js}"> </script>"""
            return code

        # Collect
        db_components = cls.db.all()
        components = []
        style = []
        for xyz in db_components:
            components.append(
                f"""{cls.package_name}['{ xyz["name"] }'] = { xyz["code_component"] }""".strip()
            )
            style.append(xyz["code_style"])

        # Minify
        code = js_minify("\n".join(components))
        css_code = cls.scss("\n".join(style))

        # Return
        return cls.live_script(code) + "\n" + f"<style>{ css_code }</style>"

    @classmethod
    def save(cls) -> str:
        """
        Save Preact components.

        Returns:
            str: Transformed JavaScript code.
        """
        # Collect
        db_components = cls.db.all()
        components = []
        style = []
        for xyz in db_components:
            components.append(
                f"""{cls.package_name}['{ xyz["name"] }'] = { xyz["code_component"] }""".strip()
            )
            style.append(xyz["code_style"])

        # Minify
        code = js_minify("\n".join(components))
        css_code = cls.scss("\n".join(style))

        # ID
        xid = str(uuid.uuid4()).replace("-", "")
        config = types.SimpleNamespace(
            js=f"index-{xid}.min.js",
            css=f"style-{xid}.min.css",
        )

        static_dir = cls.path_build()
        config_path = cls.path_config()

        # Clean Folder
        cls.remove_files(static_dir)

        # Write (Config)
        with open(config_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(config.__dict__, indent=4, sort_keys=True))

        # Write (JavaScript)
        with open(static_dir / config.js, "w", encoding="utf-8") as file:
            file.write(cls.global_var(code))

        # Write (Style)
        with open(static_dir / config.css, "w", encoding="utf-8") as file:
            file.write(css_code)

    @classmethod
    def get_config(cls):
        data = {"js": None, "css": None}
        try:
            file_path = cls.path_config()
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.loads(file.read())
        except:
            data = {"js": None, "css": None}
        return types.SimpleNamespace(**data)

    @classmethod
    def path_build(cls):
        return cls.static_dir / "app"

    @classmethod
    def path_config(cls):
        static_dir = cls.path_build()
        return static_dir / "config.json"

    @staticmethod
    def remove_files(folder_path):
        """Clean App Folder"""
        try:
            # Remove all files
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def remove_folder(folder_path):
        """Remove Component Folder"""
        try:
            # Remove all files in the folder
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            # Remove the folder itself
            shutil.rmtree(folder_path)
            print(f"Deleted: {folder_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def add_folder(folder_path):
        """Create Component Folder"""
        unzip_component(folder_path)
        print(f"Created: {folder_path}")

    @classmethod
    def api(cls, action, name):
        """Create Component Folder"""
        if action == "create":
            print(f"Creating. . . <x-{name} />")
            cls.add_folder(cls.template_dir / name)
        elif action == "delete":
            print(f"Deleting. . . <x-{name} />")
            cls.remove_folder(cls.template_dir / name)
