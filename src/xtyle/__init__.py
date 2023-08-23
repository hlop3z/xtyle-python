"""
Module: Xtyle (Toolkit)

Utilities for working with { Preact } components.

Usage:
- `xtyle.jsx` Render JSX String
- `xtyle.scss` Render SCSS String
"""


# Python
import functools
import pathlib

# Extras
import sass
from css_html_js_minify import js_minify
from py_mini_racer import MiniRacer

BASE_DIR = pathlib.Path(__file__).parent


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


jsx_compile = initialize()


def jsx(code):
    """JSX Render"""
    return js_minify(jsx_compile(code))


def scss(code):
    """SCSS Render"""
    return sass.compile(string=code, output_style="compressed")
