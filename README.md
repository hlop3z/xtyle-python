# Xtyle

Python (**JSX-Toolkit**) Documentation

## Introduction

Welcome to the Xtyle! This tool allows you to work with JSX components.

It is **powered by**.

- Python: `py-mini-racer`, `css-html-js-minify`, and `libsass`
- JavaScript: `babel`, and `prettier`

## Install

```python
pip install "xtyle"
```

## Install for Development

```python
pip install "xtyle[debug]"
```

## Example (**JSX**)

```python
import xtyle

code_js = xtyle.jsx("const App = () => <div>Hello World</div>")

print(code_js)
```

## Example (**SCSS**)

```python
import xtyle

code_css = xtyle.scss("$color: red; body { color: $color; }")

print(code_css)
```

## [Get Server and Learn More...](https://github.com/hlop3z/xtyle-server)

## Example (**Client**)

```python
import xtyle

engine = xtyle.client("http://localhost:3000")


engine.component(
    name="kebab-case-name",
    code="TypeScript Code",
    props="TypeScript Code",
    style="SASS/SCSS Code",
    docs="TypeScript Code",
)

engine.plugin(
    name="myPlugin",
    components=[
        dict(
            name="kebab-case-name",
            code="TypeScript Code",
            props="TypeScript Code",
            style="SASS/SCSS Code",
            docs="TypeScript Code",
        )
    ],
    install=dict(
        init="export default list",
        store="export default dict",
        globals="export default dict",
        directives="export default dict",
    ),
)
```

## Example (**Client-Extended**)

```python
import xtyle

engine = xtyle.client("http://localhost:3000")

def create_component(name):
    return {
        "name": name,
        "code": "\nexport default function Component(props: Props = {}) {\n  return (\n    <div x-html {...props} class={[$NAME, props.class]}>\n      {props.children}\n    </div>\n  );\n}\n",
        "style": "\n$color: red;\n.#{$NAME} { color: $color; }\n",
        "props": "\ntype Props = {\n  class?: string | string[] | object;\n  style?: string | string[] | object;\n  children?: any;\n};\n\nexport default Props;\n",
        "docs": "\n/**\n * Component - This is a my component.\n */\n",
    }


one_component = create_component("alert")
example_components = [
    create_component("alert"),
    create_component("custom-button"),
]

plugin_name = "myPlugin"
install_code = {"init": """export default [() => console.log("Plugin INIT")]"""}

# Component
demo_component = engine.component(**one_component)

# Plugin
demo_plugin = engine.plugin(plugin_name, example_components, install_code)

print(demo_component)
print("\n\n")
print(demo_plugin)
```

## Browser Usage

```html
<!-- Babel & Prettier -->
<script src="https://cdn.jsdelivr.net/gh/hlop3z/xtyle-python@main/src/xtyle/babel.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/hlop3z/xtyle-python@main/src/xtyle/prettier-full.min.js"></script>
```
