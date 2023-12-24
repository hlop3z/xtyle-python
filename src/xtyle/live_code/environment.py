import os
import shutil
import time
import uuid
import pathlib
import json

from types import SimpleNamespace

from markupsafe import Markup

from ..core import scss
from ..external_plugins import sqlow, sqlow_available
from .get_xtyle import get_xtyle_declarations

from .esmodules import ESModuleBuilder
from .sample import templates_tools
from .typescript_tools import parse_type, jinja_render
from .templates import Template
from .core import Environment, Theme, MODULE_NAME
from .types import (
    Component,
    View,
    Plugin,
    Style,
    Base,
    Cache,
    Declaration,
    Module,
    Store,
    Props,
    Sample,
    JinjaTemplate,
    schema,
    SAMPLE_CODE_LABEL,
    SAMPLE_CODE_DEFAULT,
    SAMPLE_CODE_LANGUAGES,
    COMPONENT_SAMPLE_NAMES,
)


module_sampe = SimpleNamespace()

module_sampe.init = """
export default {
    before: [],
    after: [],
};
"""

module_sampe.models = """
// Use `{ $root: true }` to create a root model. 
export default {
    $ref: {}
};
"""

module_sampe.router = """
export default {
    before({ commit /*commit, redirect, prev, next*/ }) {
        commit();
        // redirect("/login");
    },
    after({ /* prev, next */ }) {
        // console.log(next);
    },
};
"""


def process_scss(code):
    if code:
        try:
            return scss(code)
        except:
            pass
    return code or ""


def generate_unique_id():
    # Get the current timestamp in nanoseconds
    current_timestamp_ns = time.time_ns()

    # Generate a UUID4 and convert it to a string
    unique_id = str(uuid.uuid4())

    # Concatenate the timestamp and UUID to create a unique ID
    result_id = f"{unique_id.replace('-', '')}{current_timestamp_ns}"

    return result_id


def reset_folder(folder_path):
    try:
        # Check if the folder exists
        if os.path.exists(folder_path):
            # Remove all files and subdirectories in the folder
            shutil.rmtree(folder_path)
    except Exception as e:
        print(f"Error: {e}")


class XtyleEnvironment:
    schema = schema

    def __init__(
        self,
        base_dir: str = None,
        static_dir=None,
        templates_dir=None,
        static_method=None,
        reverse_method=None,
        xtyle_client=None,
    ):
        # Environment Folder
        env_dir = base_dir / ".xtyle_db"

        # Connects to NodeJS Server
        self.xtyle_client = xtyle_client

        # Core Paths
        self.base_dir = base_dir
        self.static_dir = static_dir or base_dir / "static"
        self.templates_dir = templates_dir or base_dir / "templates"

        # Environment Paths
        self.path_env_dir = env_dir
        self.path_env_core_database = env_dir / "xtyle.sqlite3"
        self.path_env_databases_dir = env_dir / ".xtyle"
        self.path_env_exports_dir = env_dir / "exports"
        self.path_env_tmp_dir = env_dir / ".tmp"

        # ESBuilder
        self.esmodule = ESModuleBuilder(self.path_env_exports_dir)

        # Base Html
        self.base_html = self.templates_dir / "base.html"

        self._init_folders()
        self._init_environment()

        self.jinja = Template(
            self.templates_dir,
            static_method=static_method,
            reverse_method=reverse_method,
        )

        # TypeScript Customization With Jinja
        self._global_types = lambda x: x

    @property
    def env(self):
        return self.environment

    @property
    def global_types(self):
        return self._global_types

    @property
    def global_plugin_cache_name(self):
        return MODULE_NAME + "__development__global__plugin__cache__key"

    @property
    def global_declarations_cache_name(self):
        return MODULE_NAME + "__development__global__declarations__cache__key"

    def _init_folders(self):
        for item in [
            "base_dir",
            "static_dir",
            "templates_dir",
            "path_env_dir",
            "path_env_databases_dir",
            "path_env_exports_dir",
            "path_env_tmp_dir",
        ]:
            current = getattr(self, item, None)
            if current:
                current.mkdir(parents=True, exist_ok=True)

    def environment_module(self, name: str):
        database = sqlow(self._module_database_path(name))
        table = lambda model: database()(model)()
        return Theme(
            component=table(Component),
            view=table(View),
            plugin=table(Plugin),
            style=table(Style),
        )

    def _init_environment(self):
        # Main Database
        database = sqlow(self.path_env_core_database)
        table = lambda model: database()(model)()
        self.environment = Environment(
            base=table(Base),
            cache=table(Cache),
            declaration=table(Declaration),
            module=table(Module),
            plugin=table(Plugin),
            store=table(Store),
            style=table(Style),
            props=table(Props),
            sample=table(Sample),
            jinja=table(JinjaTemplate),
        )
        # After Init
        if not self.environment.cache.get_by(name=self.global_plugin_cache_name):
            self.environment.cache.set(name=self.global_plugin_cache_name, build_id=0)
        if not self.environment.cache.get_by(name=self.global_declarations_cache_name):
            self.environment.cache.set(
                name=self.global_declarations_cache_name, build_id=0
            )
        if not self.environment.declaration.get_by(name=MODULE_NAME):
            xtyle_code = get_xtyle_declarations()
            self.environment.declaration.set(name=MODULE_NAME, code=xtyle_code)
            self.cache_environment_declarations()

        # Sample Code
        all_samples = self.environment.sample.all()
        all_samples_names = [item["name"] for item in all_samples]
        for name, lang in SAMPLE_CODE_LANGUAGES.items():
            if name not in all_samples_names:
                self.environment.sample.set(
                    name=name,
                    language=lang,
                    label=SAMPLE_CODE_LABEL.get(name),
                    code=SAMPLE_CODE_DEFAULT.get(name),
                )

    def get(self, model: str, name: str, module=None):
        table = self._get_table(model, module=module)
        return table.get_by(name=name)

    def all(self, model: str, module=None):
        table = self._get_table(model, module=module)
        return table.all()

    def set(self, model: str, data: dict, module=None):
        try:
            table = self._get_table(model, module=module)
            table.set(**data)
            return True
        except Exception as e:
            print(e)
            return False

    def rename(self, model: str, data: dict, module=None):
        data_old = data.get("old")
        data_new = data.get("new")
        if data_old and data_new:
            try:
                table = self._get_table(model, module=module)
                table.rename(data_old, data_new)
                return True
            except Exception as e:
                print(e)
                pass
        return False

    def delete(self, model: str, name: str, module=None):
        if model == "module":
            found = self.environment.module.get_by(name=name)
            if found:
                self.environment.cache.delete(name=str(found.get("id")))
                self.destroy(name)
        try:
            table = self._get_table(model, module=module)
            table.delete(name=name)
            return True
        except Exception as e:
            print(e)
            pass

        return False

    def drop(self, model: str, module=None):
        try:
            table = self._get_table(model, module=module)
            table.drop()
            return True
        except Exception as e:
            print(e)
            pass
        return False

    def destroy(self, module: str = None):
        try:
            if module:
                file_path = self._module_database_path(module)
            else:
                file_path = self.env_database_file
            # Remove
            os.remove(file_path)
            return True
        except OSError as e:
            return False

    def clone_module(self, src: str, dst: str):
        try:
            src_path = self._module_database_path(src)
            dst_path = self._module_database_path(dst)
            shutil.copy2(src_path, dst_path)
            return True
        except OSError as e:
            return False

    def clone_row(self, model: str, data: dict, module=None):
        table = self._get_table(model, module=module)
        data_old = data.get("old")
        data_new = data.get("new")
        updated_dict = None
        if data_old and data_new:
            updated_dict = table.get(data_old)
            if updated_dict:
                updated_dict.update({"name": data_new})
                table.set(**updated_dict)
                return updated_dict
        return None

    def _module_database_path(self, name: str):
        model = self.env.module.get_by(name=name)

        if not model:
            self.env.module.set(name=name)
            model = self.env.module.get_by(name=name)

        db_id = model.get("id")
        return self.path_env_databases_dir / f"{db_id}.sqlite3"

    def _get_table(self, model: str, module=None):
        if not module:
            db = self.env._asdict()
            table = db.get(model)
        else:
            if not self.env.module.get(module):
                self.env.module.set(name=module)
            db = self.environment_module(module)._asdict()
            table = db.get(model)
        return table

    def sample_component(self):
        all_samples = self.all("sample")
        dict_input = {
            item.get("name"): item.get("code")
            for item in all_samples
            if item.get("name") in COMPONENT_SAMPLE_NAMES
        }
        return dict_input

    def sample_module(self):
        basic_code = "export default {};"
        dict_input = {
            "is_global": False,
            "merge": True,
            "actions": basic_code,
            "directives": basic_code,
            "globals": basic_code,
            "init": module_sampe.init.strip(),
            "models": module_sampe.models.strip(),
            "router": module_sampe.router.strip(),
            "store": basic_code,
        }
        return dict_input

    def get_base_html(self):
        return self.get_or_create_file(self.base_html)

    def set_base_html(self, text: str = ""):
        with open(self.base_html, "w") as file:
            file.write(text)
        return True

    def get_or_create_file(self, file_path):
        if os.path.exists(file_path):
            # File exists, open and return its contents
            with open(file_path, "r") as file:
                return file.read()
        else:
            # File doesn't exist, create a blank one
            with open(file_path, "w") as file:
                file.write("")
            return ""

    def _global_props_types(self):
        all_props = self.all("props")
        create_type = lambda x: "\n" + (parse_type(x.get("code", "")).props or "")
        return {x.get("name"): create_type(x) for x in all_props}

    def global_props_types(self):
        all_props = self._global_props_types()
        self._global_types = lambda code_props: jinja_render(
            code_props or "", **all_props
        )
        return lambda code_props: jinja_render(code_props or "", **all_props)

    def build_module(self, package_name):
        the_plugin = self.build_components(package_name)
        if the_plugin:
            the_styles = self.build_styles(package_name, the_plugin.style)

            return SimpleNamespace(
                name=package_name,
                style=the_styles,
                javascript=the_plugin.javascript,
                declarations=the_plugin.declarations,
            )
        return None

    def build_styles(self, package_name, components_style: str = None):
        # TODO
        styles = self.all("style", package_name)
        final_style = "\n".join([process_scss(x.get("code")) for x in styles])
        if self.xtyle_client:
            return self.xtyle_client.css(final_style + (components_style or ""))
        return final_style

    def build_views(self, package_name):
        self.global_props_types()
        _components_list = self.all("view", package_name)
        components_list = []
        views_dict = {}
        generic_variable_name = "installed_views"
        if len(_components_list) > 0:
            for item in _components_list:
                build = self._build_component(item, generic_variable_name, True)
                if build:
                    components_list.append(build.__dict__)
                    pascal_name = build.name.title().replace("-", "")
                    views_dict[item.get("path")] = pascal_name
            if self.xtyle_client:
                final_plugin = self.xtyle_client.plugin(
                    "installed_views",
                    components_list,
                    None,
                )
                if final_plugin:
                    final_plugin_style = final_plugin.get("style", "")
                    if not final_plugin_style.strip() == "":
                        final_plugin_style = f"""xtyle.util.inject(`{final_plugin_style}`, "xtyle_installed_views")"""
                    js_dict_out = ""
                    for key, val in views_dict.items():
                        js_dict_out += f"""xtyle.view("{key}", "{val}", installed_views.{val});\n"""

                    return SimpleNamespace(
                        name=package_name,
                        key="installed_views",
                        javascript=self.xtyle_client.minify(
                            final_plugin.get("javascript")
                            + "\n"
                            + final_plugin_style
                            + "\n"
                            + js_dict_out
                        ),
                    )
        return None

    def build_components(self, package_name):
        self.global_props_types()
        module_dict = self.environment.module.get_by(name=package_name)
        _components_list = self.all("component", package_name)
        components_list = []
        if module_dict:
            for item in _components_list:
                build = self._build_component(item, package_name)
                if build:
                    components_list.append(build.__dict__)
            if self.xtyle_client:
                final_plugin = self.xtyle_client.plugin(
                    package_name, components_list, module_dict
                )
                if final_plugin:
                    return SimpleNamespace(name=package_name, **final_plugin)
        return None

    def render_jinja_component(self, code_text: str, data=None):
        jinja_kwargs = data or {}
        return jinja_render(
            code_text,
            **jinja_kwargs,
        )

    def _build_component(self, _component, package_name, is_view: bool = False):
        component = SimpleNamespace(**_component)
        info = self._get_component_info(package_name, component.name)
        final_docs = None
        final_props = None
        final_code = None
        final_code = self.render_jinja_component(component.code or "", info)
        final_style = self.render_jinja_component(component.style or "", info)
        if not is_view:
            final_docs = self.render_jinja_component(component.docs or "", info)
            final_props = self.global_types(component.props or "")
        return SimpleNamespace(
            name=component.name,
            code=final_code,
            style=final_style,
            docs=final_docs,
            props=final_props,
        )

    def _get_component_info(self, package, component):
        package_name = (package or "package").lower().replace("-", "_")
        component_name = (component or "component").title().replace("-", "")
        return {
            "package": package_name,
            "name": component_name,
            "class": f"{package_name}__{component_name}",
            "this": f"{package_name}.{component_name}",
        }

    def cache_custom_module(self, package_name):
        module_dict = self.get("module", package_name)
        module_name = str(module_dict.get("id"))

        my_plugin = self.build_module(package_name)
        my_views = self.build_views(package_name)
        data_dict = {}
        if my_plugin:
            data_dict = {"name": module_name, "build_id": 0}
            found = self.environment.cache.get_by(name=module_name)
            if found:
                data_dict.update(found)
                data_dict["build_id"] = data_dict.get("build_id", 0)

            # Module
            data_dict["module"] = {
                "style": my_plugin.style,
                "javascript": my_plugin.javascript,
            }
            data_dict["declarations"] = my_plugin.declarations or ""
        # Views
        if my_views:
            data_dict["views"] = my_views.__dict__

        data_dict["build_id"] += 1
        self.environment.cache.set(**data_dict)

    def cache_environment_plugin(self):
        all_the_plugins = self.environment.plugin.all()

        plugin_names = set()
        style_list = []
        script_list = []
        declarations_list = []
        data_dict = {}
        plugin_dict = {}

        cache_name = self.global_plugin_cache_name
        data_dict = {"name": cache_name}

        found = self.environment.cache.get_by(name=cache_name)
        if found:
            data_dict.update(found)
            data_dict["build_id"] = data_dict.get("build_id", 0)

        for item in all_the_plugins:
            plugin_names.add(item.get("name"))
            style_list.append(item.get("style", ""))
            script_list.append(item.get("javascript", ""))
            declarations_list.append(item.get("declarations", ""))

        plugin_dict["names"] = list(plugin_names)
        plugin_dict["style"] = "\n".join(style_list)
        plugin_dict["javascript"] = "\n".join(script_list)

        data_dict["declarations"] = "\n".join(declarations_list)
        data_dict["plugins"] = plugin_dict
        data_dict["build_id"] += 1
        self.environment.cache.set(**data_dict)

    def cache_environment_declarations(self):
        all_the_declarations = self.environment.declaration.all()
        declarations_list = []

        cache_name = self.global_declarations_cache_name
        data_dict = {"name": cache_name}

        found = self.environment.cache.get_by(name=cache_name)
        if found:
            data_dict.update(found)
            data_dict["build_id"] = data_dict.get("build_id", 0)

        for item in all_the_declarations:
            declarations_list.append(item.get("code", ""))

        data_dict["declarations"] = "\n".join(declarations_list)
        data_dict["build_id"] += 1
        self.environment.cache.set(**data_dict)

    def cached_environment(self):
        plugins = self.environment.cache.get_by(name=self.global_plugin_cache_name)
        declarations = self.environment.cache.get_by(
            name=self.global_declarations_cache_name
        )
        return SimpleNamespace(
            plugins=SimpleNamespace(
                build_id=plugins.get("build_id"),
                code=plugins.get("declarations"),
            ),
            declarations=SimpleNamespace(
                build_id=declarations.get("build_id"),
                code=declarations.get("declarations"),
            ),
        )

    def get_preview_cached(self, module_name: str):
        _module = self.environment.module.get_by(name=module_name)
        _plugins = self.environment.cache.get_by(name=self.global_plugin_cache_name)
        plugins = {}
        module = {}
        views = {}
        template_string = None
        if _plugins:
            plugins = _plugins.get("plugins")
        if _module:
            module_cached = self.environment.cache.get_by(name=str(_module.get("id")))
            template_base_id = _module.get("base_id")
            if template_base_id:
                template = self.environment.base.get_by(id=template_base_id)
                template_string = template.get("code")
            if module_cached:
                module_dict = module_cached.get("module", {})
                module["style"] = module_dict.get("style")
                module["javascript"] = module_dict.get("javascript")
                # Views
                views["javascript"] = module_cached.get("views", {}).get("javascript")
        return SimpleNamespace(
            template=template_string,
            context={
                "views": views,
                "module": module,
                "plugins": plugins,
            },
        )

    def get_global_cached(self, input_data: dict = None):
        input_data = input_data or {}
        module_input = input_data.get("module", {})

        # Global Cached
        plugins_input = input_data.get("plugins", {})
        declarations_input = input_data.get("declarations", {})
        cached_plugins_id = plugins_input.get("build_id", 0)
        cached_declarations_id = declarations_input.get("build_id", 0)
        cached = self.cached_environment()
        cache_dict = {"plugins": None, "declarations": None, "module": None}
        if cached_plugins_id != cached.plugins.build_id:
            cache_dict["plugins"] = cached.plugins.__dict__
        if cached_declarations_id != cached.declarations.build_id:
            cache_dict["declarations"] = cached.declarations.__dict__

        # Current Module
        cached_module = self.environment.cache.get_by(
            name=str(module_input.get("module_id", 0))
        )
        if cached_module:
            cached_module_id_db = cached_module.get("build_id", 0)
            cached_module_id = module_input.get("build_id", 0)
            if cached_module_id != cached_module_id_db:
                module_input["build_id"] = cached_module.get("build_id")
                module_input["code"] = cached_module.get("declarations")
                cache_dict["module"] = module_input
        return cache_dict

    def rows_for_tables(
        self,
        model,
        module_name=None,
        fields=["id", "name", "path", "label", "language", "version"],
    ):
        output = []
        for item in self.all(model, module_name):
            output.append({k: v for k, v in item.items() if k in fields})
        return output

    @property
    def init_template(self):
        return Markup(templates_tools.init_html.text)

    def jinja_preview_template(
        self, url: str, module: str, view: str, data: dict, extra: dict = None
    ):
        context = {}
        if extra:
            context.update(extra)
        if view and module:
            view_name_title = view.title().replace("-", "")
            context["module_name"] = module
            context["preview_name"] = view_name_title
            context["preview_url"] = f"{url}?module={module}&view={view}"
            context["preview_data"] = data

        return Markup(jinja_render(templates_tools.dev_html.text, **context))

    @staticmethod
    def js_xtyle_use_plugin(names):
        names = names or []
        use = lambda name: "try { xtyle.use(" + name + "); } catch(e){};"
        plugins = [use(name) for name in names]
        return "\n".join(plugins)

    def collect_plugins(self):
        _plugins = (
            self.environment.cache.get_by(name=self.global_plugin_cache_name) or {}
        )
        plugins = _plugins.get("plugins", {}) or {}
        final_module_js = plugins.get("javascript") or ""
        final_js = (
            final_module_js + "\n" + self.js_xtyle_use_plugin(plugins.get("names"))
        )
        if final_js and self.xtyle_client:
            final_js = self.xtyle_client.minify(final_js)
        final_obj = SimpleNamespace(
            **{
                "javascript": final_js,
                "style": plugins.get("style"),
            }
        )
        if final_obj.javascript == "":
            final_obj.javascript = None
        if final_obj.style == "":
            final_obj.style = None
        return final_obj

    def _collect_applications(self):
        apps_dict = {}
        self.cache_environment_declarations()
        self.cache_environment_plugin()

        # Get Plugins
        plugins_obj = self.collect_plugins()

        # Get Apps
        for row in self.environment.module.all():
            app_id = row.get("id")
            app_name = row.get("name")
            jinja_base_id = row.get("base_id", 0)
            self.cache_custom_module(app_name)
            # ['module', 'views', 'plugins', 'declarations', 'build_id', 'id', 'name']
            found = self.environment.cache.get_by(name=str(app_id))
            the_components = found.get("module", {}) or {}
            the_views = found.get("views", {}) or {}
            if found:
                apps_dict[app_name] = SimpleNamespace(
                    **{
                        "template_id": jinja_base_id or 0,
                        "components": SimpleNamespace(
                            **{
                                "javascript": the_components.get("javascript"),
                                "style": the_components.get("style"),
                            }
                        ),
                        "views": SimpleNamespace(
                            **{
                                "javascript": the_views.get("javascript"),
                            }
                        ),
                    }
                )

        return SimpleNamespace(
            environment=plugins_obj,
            apps=apps_dict,
        )

    def collect_applications(self):
        unique_id = generate_unique_id()
        root_path = pathlib.Path("xtyle") / pathlib.Path(unique_id)
        final_app_path = root_path / pathlib.Path("apps")
        final_project = self._collect_applications()
        final_apps_dict = {}
        final_build = []
        final_bases_ids = {}
        final_bases_names = {}
        final_modules_names = set()
        with_global_javascript = False
        with_global_styles = False

        # Jinja Bases
        for item in self.environment.base.all():
            final_bases_ids[item.get("id")] = item.get("name")
            final_bases_names[item.get("name")] = item.get("code")

        # Core Parts
        if final_project.environment.javascript:
            with_global_javascript = True
            final_build.append(
                SimpleNamespace(
                    path=root_path / "index.js",
                    code=final_project.environment.javascript,
                )
            )
        if final_project.environment.style:
            with_global_styles = True
            final_build.append(
                SimpleNamespace(
                    path=root_path / "style.css",
                    code=final_project.environment.style,
                )
            )

        # Apps Parts
        for app_name, config in final_project.apps.items():
            # Get
            components_js = config.components.javascript
            components_css = config.components.style
            views_js = config.views.javascript
            # Clean
            components_js = self.clean_final_value(components_js)
            components_css = self.clean_final_value(components_css)
            views_js = self.clean_final_value(views_js)
            # Process
            final_js = components_js + "\n" + views_js
            if components_css:
                final_js += "\n" + f"xtyle.util.inject(`{components_css}`)"
            if self.xtyle_client:
                final_js = self.xtyle_client.minify(final_js)

            final_apps_dict[app_name] = final_bases_ids.get(config.template_id)
            final_build.append(
                SimpleNamespace(
                    path=final_app_path / f"{app_name}.js",
                    code=final_js,
                )
            )
            final_modules_names.add(app_name)

        meta_info = SimpleNamespace(
            id=unique_id,
            path=f"xtyle/{unique_id}",
            keys=list(final_modules_names),
            global_style=with_global_styles,
            global_script=with_global_javascript,
            apps=final_apps_dict,
            base=self.get_base_html(),
            templates=final_bases_names,
        )

        return SimpleNamespace(
            meta=meta_info,
            files=final_build,
        )

    def create_static(self):
        project = self.collect_applications()
        root_path = pathlib.Path(self.static_dir) / project.meta.path
        xtyle_path = pathlib.Path(self.static_dir) / "xtyle"
        xtyle_apps_path = root_path / "apps"

        reset_folder(xtyle_path)

        root_path.mkdir(parents=True, exist_ok=True)
        xtyle_apps_path.mkdir(parents=True, exist_ok=True)

        for file in project.files:
            with open(self.static_dir / file.path, "w", encoding="utf-8") as f:
                f.write(file.code or "")

        with open(self.base_dir / "xtyle.config.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(project.meta.__dict__))

        # Return Info
        return project.meta.__dict__

    @staticmethod
    def clean_final_value(value):
        if isinstance(value, str):
            if value.strip() == "":
                return ""
        elif value == None:
            return ""
        return value

    def export_module_zip(self, module_name: str):
        theme_dict = self.environment.module.get_by(name=module_name)
        compo_list = self.all("component", module_name)
        style_list = self.all("style", module_name)
        export_dict = {
            **theme_dict,
            "components": {},
            "styles": {item.get("name"): item.get("code") for item in style_list},
        }
        for row in compo_list:
            build = self._build_component(row, module_name)
            if build:
                data = self.xtyle_client.component(**build.__dict__, theme=module_name)
                if data:
                    name = data.get("name")
                    export_dict["components"][name] = dict(
                        index=data.get("index"),
                        style=data.get("style"),
                        docs=data.get("docs"),
                        props=data.get("props"),
                    )
        return self.esmodule.create_zip(export_dict)
        # return export_dict.get("components")
