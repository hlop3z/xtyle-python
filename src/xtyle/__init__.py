# Locals
from .client import Client
from .live_code import Environment, gzip, schema
from .core import jsx, scss, prettier
from .live_code.static import XtyleApp
from .live_code.plugin_gzip import PluginGzip


def client(host="http://localhost:3000"):
    """Xtyle Client"""
    return Client(host)


class App:
    def __init__(
        self,
        root_path: str = None,
        root: str = None,
        base_url: str = None,
        rename: dict = None,
        debug: bool = False,
        xtyle_server: str = "http://localhost:3000",
    ):
        self._devs = False

        if debug:
            self._devs = Environment(
                xtyle_client=Client(xtyle_server),
                base_dir=root_path,
            )

        # Core
        self._static = None
        self._init_static = lambda: XtyleApp(
            root_path,
            root=root,
            base_url=base_url,
            rename=rename,
        )

    @property
    def devs(self):
        return self._devs

    def render(self, __url_string__, **context):
        if not self._static:
            self._static = self._init_static()
        return self._static.render(__url_string__, **context)

    def create_static(self):
        self._devs.create_static()

    def export_module_zip(self, module_name: str):
        found = self._devs.environment.module.get_by(name=module_name)
        if found:
            return self._devs.export_module_zip(module_name)
        return None

    def module_plugin_export(self, package_name: str):
        active = self._devs.build_module(package_name)
        if active:
            return PluginGzip.compress_json(active.__dict__)
        return None

    def api_control(self, **req_dict):
        admin = self._devs
        action_name = req_dict.get("action", "all")
        model = req_dict.get("model", "component")
        input_data = req_dict.get("input", {})
        module_name = req_dict.get("module")
        response = None
        if admin:
            try:
                match action_name:
                    case "all":
                        response = admin.rows_for_tables(model, module_name)
                    case "set":
                        response = admin.set(model, input_data, module_name)
                    case "get":
                        response = admin.get(model, input_data.get("name"), module_name)
                    case "del":
                        admin.delete(model, input_data.get("name"), module_name)
                    case "create":
                        if model in ["module"]:
                            sample_module = admin.sample_module()
                            input_data.update(sample_module)
                        elif model in ["component", "view"]:
                            sample_component = admin.sample_component()
                            if model == "view":
                                sample_component = {
                                    "code": sample_component.get("code")
                                }
                            input_data.update(sample_component)
                        response = admin.set(model, input_data, module_name)
                    case "html":
                        html_method = input_data.get("method", "get")
                        html_code = input_data.get("code", "")
                        if html_method == "get":
                            response = admin.get_base_html()
                        else:
                            admin.set_base_html(html_code)
                    case "cache-declarations":
                        response = admin.get_global_cached(input_data)

                # After Updating The Database Cache The Builds
                if action_name in ["create", "set", "del"]:
                    if model == "declaration":
                        admin.cache_environment_declarations()
                    elif model == "plugin":
                        admin.cache_environment_plugin()
                    elif module_name and model not in ["declaration", "plugin"]:
                        admin.cache_custom_module(module_name)
            except Exception as e:
                print(e)
                pass
        return response
