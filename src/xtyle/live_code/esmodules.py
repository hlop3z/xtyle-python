import json
import shutil
import uuid
import zipfile

from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Template


BASE_DIR = Path(__file__).parent / "sample-codes"

ALLOWED_MODULE_FIELDS = [
    "actions",
    "directives",
    "globals",
    "init",
    "models",
    "router",
    "store",
    "docs",
]


def get_file(path, is_json=False):
    content = ""
    with open(BASE_DIR / path, "r", encoding="utf-8") as file:
        content = file.read()
    if is_json:
        content = json.loads(content)
    return content


class ESModuleBuilder:
    def __init__(self, base_dir, delete_threshold_minutes: int = 10):
        package_json = get_file("package.json", is_json=True)
        self.threshold_minutes = delete_threshold_minutes
        self.base_dir = base_dir
        # LOAD TEMPLATES
        self.xtyle_library_declarations = get_file("globals.d.ts")
        self.xtyle_library_html = get_file("index.html")
        self.xtyle_library_index = Template(get_file("index.ts"))
        self.xtyle_package_json = lambda name: {"name": name, **package_json}
        self.xtyle_postcss_config_cjs = get_file("postcss.config.cjs")
        self.xtyle_library_preview = get_file("preview.ts")
        self.xtyle_rollup_config_js = get_file("rollup.config.js")
        self.xtyle_typescript_json_config = get_file("tsconfig.json")
        self.xtyle_typescript_json_config_node = get_file("tsconfig.node.json")
        self.xtyle_vite_typescript = get_file("vite-env.d.ts")
        self.xtyle_vite_config_js = get_file("vite.config.js")
        self.xtyle_scss_loader = get_file("globals.d.ts")
        self.xtyle_build_mjs = get_file("xtyle_build.mjs")
        self.xtyle_startapp_mjs = get_file("xtyle_component.mjs")

    def generate_folders_zip(self):
        # TMP
        tmp_name = str(uuid.uuid4())
        tmp_path = self.base_dir
        # Module
        module_main_path = tmp_path / tmp_name
        src_path = module_main_path / "src"
        app_folder = src_path / "app"
        component_folder = src_path / "components"
        styles_folder = src_path / "styles"
        # INIT
        tmp_path.mkdir(parents=True, exist_ok=True)
        module_main_path.mkdir(parents=True, exist_ok=True)
        app_folder.mkdir(parents=True, exist_ok=True)
        component_folder.mkdir(parents=True, exist_ok=True)
        styles_folder.mkdir(parents=True, exist_ok=True)
        return SimpleNamespace(
            name=tmp_name,
            tmp=tmp_path,
            base=module_main_path,
            src=src_path,
            components=component_folder,
            app=app_folder,
            styles=styles_folder,
        )

    def create_component_files(self, core, component_name, data):
        component_folder = core.components / component_name
        component_folder.mkdir(parents=True, exist_ok=True)
        for file_name, content in data.items():
            file_extension = "tsx" if file_name != "style" else "scss"
            file_path = component_folder / f"{file_name}.{file_extension}"

            with open(file_path, "w") as file:
                if file_name == "index":
                    file.write("""import "./style.scss";\n""" + (content or ""))
                else:
                    file.write(content or "")

    def create_app_files(self, core, data):
        for file_name, content in data.items():
            file_extension = "ts"
            file_path = core.app / f"{file_name}.{file_extension}"

            with open(file_path, "w") as file:
                file.write(content or "export default {}")

    def create_styles(self, core, data):
        styles = []
        for file_name, content in data.items():
            file_extension = "scss"
            file_path = core.styles / f"{file_name}.{file_extension}"

            if content and content != "":
                with open(file_path, "w") as file:
                    file.write(content)
                styles.append(f'''import "./styles/{file_name}.{file_extension}"''')
        return "\n".join(styles)

    def create_plugin_tmp(self, core_paths, data):
        components_dict = data.get("components", {})
        styles_dict = data.get("styles", {})
        export_list = []

        self.create_app_files(
            core_paths,
            {key: value for key, value in data.items() if key in ALLOWED_MODULE_FIELDS},
        )
        styles_string = self.create_styles(
            core_paths,
            styles_dict,
        )

        for component_name, component_data in components_dict.items():
            self.create_component_files(core_paths, component_name, component_data)
            export_list.append(self.component_export_string(component_name))

        file_contents = [
            # Components
            (core_paths.components / "index.ts", "\n".join(export_list)),
            # Core
            (
                core_paths.src / "index.ts",
                self.xtyle_library_index.render(styles=f"\n{styles_string}"),
            ),
            (core_paths.src / "preview.ts", self.xtyle_library_preview),
            (core_paths.src / "vite-env.d.ts", self.xtyle_vite_typescript),
            (core_paths.base / "index.html", self.xtyle_library_html),
            (core_paths.base / "globals.d.ts", self.xtyle_library_declarations),
            (core_paths.base / "vite.config.js", self.xtyle_vite_config_js),
            (core_paths.base / "tsconfig.json", self.xtyle_typescript_json_config),
            (
                core_paths.base / "tsconfig.node.json",
                self.xtyle_typescript_json_config_node,
            ),
            (core_paths.base / "rollup.config.js", self.xtyle_rollup_config_js),
            (core_paths.base / "postcss.config.cjs", self.xtyle_postcss_config_cjs),
            (core_paths.base / "xtyle_build.mjs", self.xtyle_build_mjs),
            (core_paths.base / "xtyle_component.mjs", self.xtyle_startapp_mjs),
            (
                core_paths.base / "package.json",
                json.dumps(self.xtyle_package_json(data.get("name")), indent=4),
            ),
        ]
        self.write_files(file_contents),

    @staticmethod
    def write_files(file_contents):
        for file_path, content in file_contents:
            with open(file_path, "w") as file:
                file.write(content)

    @staticmethod
    def component_export_string(component_name):
        return f'export {{ default as {component_name} }} from "./{component_name}/index.tsx";'

    def delete_old_files(self, folder_path):
        threshold_minutes = self.threshold_minutes
        now = datetime.now()
        threshold_time = now - timedelta(minutes=threshold_minutes)

        folder_path = Path(folder_path)

        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                file_created_time = datetime.fromtimestamp(file_path.stat().st_ctime)

                if file_created_time < threshold_time:
                    try:
                        file_path.unlink()
                    except:
                        pass

            elif file_path.is_dir():
                dir_created_time = datetime.fromtimestamp(file_path.stat().st_ctime)

                if dir_created_time < threshold_time:
                    try:
                        shutil.rmtree(file_path)
                    except:
                        pass

    def create_zip(self, data):
        core = self.generate_folders_zip()
        self.create_plugin_tmp(core, data)

        zip_file_name = f"{core.name}.zip"
        final_path = core.tmp / zip_file_name

        with zipfile.ZipFile(final_path, "w") as zip_file:
            for file_path in core.base.rglob("*"):
                arcname = str(file_path.relative_to(core.base))
                zip_file.write(file_path, arcname)

        shutil.rmtree(core.base)
        self.delete_old_files(core.tmp)
        return final_path
