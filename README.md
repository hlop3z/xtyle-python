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

## Browser Usage

```html
<!-- Babel & Prettier -->
<script src="https://cdn.jsdelivr.net/gh/hlop3z/xtyle-python@main/src/xtyle/babel.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/hlop3z/xtyle-python@main/src/xtyle/prettier.min.js"></script>
```
