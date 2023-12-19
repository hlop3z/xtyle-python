import pytest

# Testing
import xtyle

def create_component(name):
    return {
        "name": name,
        "code": "\nexport default function Component(props: Props = {}) {\n  return (\n    <div x-html {...props} class={[$NAME, props.class]}>\n      {props.children}\n    </div>\n  );\n}\n",
        "style": "\n$color: red;\n.#{$NAME} { color: $color; }\n",
        "props": "\ntype Props = {\n  class?: string | string[] | object;\n  style?: string | string[] | object;\n  children?: any;\n};\n\nexport default Props;\n",
        "docs": "\n/**\n * Component - This is a my component.\n */\n",
    }


def test_jsx():
    code = xtyle.jsx("const App = () => <div>Hello World</div>")
    assert code.strip() == """const App = () => h("div", null, "Hello World");"""



def test_scss():
    code = xtyle.scss("$color: red; body { color: $color; }")
    assert code.strip() == """body{color:red}"""


def test_client_component():
    code = xtyle.scss("$color: red; body { color: $color; }")
    assert code.strip() == """body{color:red}"""


def test_client_plugin():
    engine = xtyle.client("http://localhost:3000")

    one_component = create_component("alert")

    # Component
    demo_component = engine.component(**one_component)

    assert demo_component == {
        "name": "Alert",
        "index": 'const $NAME = "Alert";\n\nexport default function Component(props: Props = {}) {\n  return (\n    <div x-html {...props} class={[$NAME, props.class]}>\n      {props.children}\n    </div>\n  );\n}\n',
        "style": '$NAME: "Alert";\n\n$color: red;\n.#{$NAME} { color: $color; }\n',
        "props": "\ntype Props = {\n  class?: string | string[] | object;\n  style?: string | string[] | object;\n  children?: any;\n};\n\nexport default Props;\n",
        "docs": "\n/**\n * Component - This is a my component.\n */\n",
        "buildIndex": 'const Alert=function(l={}){return h("div",{"x-html":!0,...l,class:["Alert",l.class]},l.children)};',
        "buildStyle": ".Alert{color:red}",
        "declaration": "/**\n * Component - This is a my component.\n */\nAlert: (props: {\n  class?: string | string[] | object;\n  style?: string | string[] | object;\n  children?: any;\n}) => object;",
    }


def test_client_plugin():
    engine = xtyle.client("http://localhost:3000")

    plugin_name = "myPlugin"
    install_code = {"init": """export default [() => console.log("Plugin INIT")]"""}

    # Components
    example_components = [
        create_component("alert"),
        create_component("custom-button"),
    ]

    # Plugin
    demo_plugin = engine.plugin(plugin_name, example_components, install_code)
    
    assert demo_plugin == {
        "javascript": 'var myPlugin={Alert:function(t={}){return h("div",{"x-html":!0,...t,class:["Alert",t.class]},t.children)},CustomButton:function(t={}){return h("div",{"x-html":!0,...t,class:["CustomButton",t.class]},t.children)},install:function(t,l){return{init:[()=>console.log("Plugin INIT")],store:void 0,globals:void 0,directives:void 0}}};',
        "style": ".Alert,.CustomButton{color:red}",
        "declarations": "declare const myPlugin: {\n/**\n * Component - This is a my component.\n */\nAlert: (props: {\n  class?: string | string[] | object;\n  style?: string | string[] | object;\n  children?: any;\n}) => object;\n\n/**\n * Component - This is a my component.\n */\nCustomButton: (props: {\n  class?: string | string[] | object;\n  style?: string | string[] | object;\n  children?: any;\n}) => object;\n}",
    }
