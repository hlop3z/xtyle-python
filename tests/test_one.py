import pytest

# Testing
import xtyle


def test_jsx():
    code = xtyle.jsx("const App = () => <div>Hello World</div>")
    assert code.strip() == """const App=()=>h("div",null,"Hello World");"""


def test_scss():
    code = xtyle.scss("$color: red; body { color: $color; }")
    assert code.strip() == """body{color:red}"""
