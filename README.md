# Xtyle

Python (**JSX-Toolkit**) Documentation

## Introduction

Welcome to the Xtyle! This tool allows you to work with JSX components.

It is **powered by**.

- Python: `py-mini-racer`, `css-html-js-minify`, and `libsass`
- JavaScript: `babel`, and `prettier`

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
