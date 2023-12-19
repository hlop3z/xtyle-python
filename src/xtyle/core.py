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
from collections import namedtuple

# Extras
from .external_plugins import MiniRacer, sass, sass_available, mini_racer_available


BASE_DIR = pathlib.Path(__file__).parent

engine = MiniRacer


Javascript = namedtuple("JavascriptInPython", ["jsx", "prettier"], module="xtyle")


def initialize() -> functools.partial:
    """
    Initialize the MiniRacer compiler for JSX transformation.

    Returns:
        functools.partial: A callable for JSX transformation.
    """
    if mini_racer_available:
        ctx = MiniRacer()

        # Files
        babel_path = BASE_DIR / "babel.min.js"
        prettier_path = BASE_DIR / "prettier-full.min.js"
        custom_path = BASE_DIR / "custom.js"

        # Babel
        with open(babel_path, "r", encoding="utf-8") as b_file:
            babel_code = b_file.read()

        # Prettier
        with open(prettier_path, "r", encoding="utf-8") as p_file:
            prettier_code = p_file.read()

        # Custom
        with open(custom_path, "r", encoding="utf-8") as c_file:
            custom_code = c_file.read()

        # Execute (babel.min.js & prettier.min.js)
        ctx.eval(babel_code)
        ctx.eval(prettier_code)
        ctx.eval(custom_code)

        return Javascript(
            jsx=functools.partial(ctx.call, "JSX"),
            prettier=functools.partial(ctx.call, "prettyCode"),
        )


jsx_compile = initialize()


def prettier(code, language=None):
    """Prettier Language"""
    if mini_racer_available:
        return jsx_compile.prettier(code, language)
    return code


def jsx(code):
    """JSX Render"""
    if mini_racer_available:
        return jsx_compile.jsx(code)
    return code


def scss(code):
    """SCSS Render"""
    if sass_available:
        return sass.compile(string=code, output_style="compressed")
    return code
