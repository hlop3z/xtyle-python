import json
from types import SimpleNamespace
from .external_plugins import requests, requests_available


class Client:
    def __init__(self, host: str = "http://localhost:3000"):
        self.host = host

    def _handle_response(self, response):
        if response.status_code == 200:
            return SimpleNamespace(data=response.json(), error=None)
        else:
            return SimpleNamespace(data=None, error=response.status_code)

    def post(self, path: str, data):
        json_data = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.host + path, data=json_data, headers=headers)
        return self._handle_response(response)

    def typescript(self, path: str, data: str) -> str:
        response = self.post(path, {"code": data})
        return (
            response.data.get("code", "")
            if response.data and not response.error
            else ""
        )

    def ping(self, **kwargs) -> SimpleNamespace:
        return self.post("/ping", kwargs)

    def tsx(self, code_string: str) -> str:
        return self.typescript("/tsx", code_string)

    def css(self, code_string: str) -> str:
        return self.typescript("/scss", code_string)

    def minify(self, code_string: str) -> str:
        return self.typescript("/minify", code_string)

    def component(
        self,
        name: str = None,
        code: str = None,
        props: str = None,
        style: str = None,
        docs: str = None,
        theme: str = None,
        **ignored,
    ) -> str:
        return self.typescript(
            "/component",
            {
                "name": name,
                "code": code,
                "props": props,
                "style": style,
                "docs": docs,
                "theme": theme,
            },
        )

    def plugin(
        self,
        name: str = None,
        components: list = None,
        install: dict = None,
        **ignored,
    ) -> str:
        return self.typescript(
            "/plugin", {"name": name, "components": components, "install": install}
        )
