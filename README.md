# Xtyle

Python (**JSX-Toolkit**) Documentation

## Introduction

Welcome to the Xtyle! This tool allows you to work with JSX components, compile them, and save them as static files for use with other frameworks like Flask. It is powered by `py-mini-racer`, `css-html-js-minify`, and `libsass`.

## Getting Started

To get started with the JSX Python Tool, follow these steps:

1. **Initialization:** Initialize the JSX engine using `JSX.init(BASE_DIR)` where `BASE_DIR` is the base directory for your project.

2. **Loading Components:** Load a JSX component folder using `JSX.component(component_name)`. This will allow you to work with the specified component.

3. **Compilation and Saving:** Compile the loaded component, and save the compiled JavaScript and CSS files using `JSX.save()`.

4. **API:** Use the API to create or delete components using `JSX.api(action, component_name)`. Available actions are "create" and "delete".

5. **Build Configuration:** Use `JSX.build()` to build your components. This can be useful for printing or further processing.

6. **Config File:** To use the saved static files with other tools like Flask, you can load the configuration file using `JSX.get_config()`.

## Examples

Here's an example of how to use the JSX Python Tool:

```python
from pathlib import Path
from xtyle import JSX

# Root Path
BASE_DIR = Path(__file__).parent

# Initialize the JSX engine
JSX.init(BASE_DIR)

# Load and work with a component
JSX.component("hello-world")

# Create and delete components using the API
JSX.api("create", "button")
JSX.api("delete", "button")

# Save compiled files
JSX.save()
```

## Flask Example

### Python

```python
from flask import Flask, render_template
from xtyle import JSX

# Base Folder
BASE_DIR = Path(__file__).parent

# Initialize the JSX engine
JSX.init(BASE_DIR)

# Initialize Flask App
app = Flask(__name__)

# Routes
@app.route("/")
def index():
    return render_template(
        "index.html",
        jsx=JSX.components,
        jsx_code=JSX.dev,
    )
```

### HTML

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My Flask App</title>

    <!-- Xtyle (JS) -->
    <script
      src="https://unpkg.com/xtyle@latest"
      type="text/javascript"
    ></script>

    <!-- Components -->
    {{ jsx("demo", "hello-world") }}

    <!-- JSX Code -->
    {{ jsx_code() | safe }}
  </head>

  <body>
    <script type="text/javascript">
      /* @Register */
      xtyle.use({
        elements: GUI,
      });

      /* @Router */
      const router = {
        history: false,
        baseURL: null,
      };

      /* @Render */
      xtyle.init(GUI.demo, document.body, router);
    </script>
  </body>
</html>
```
