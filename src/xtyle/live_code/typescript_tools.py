import re
from types import SimpleNamespace
from jinja2 import Template
import json
from markupsafe import Markup


DEFAULT_OUTPUT = {"props": "", "output": ""}


def parse_type_props(type_string):
    regex = re.compile(r"type Props\s*=\s*(?:\(\s*\))?{([\s\S]+?)};?")
    match = regex.search(type_string)

    if match:
        props = match.group(1).strip()
        return {"props": props or "", "output": "any"}

    return {**DEFAULT_OUTPUT}


def parse_type_method(type_string):
    regex = re.compile(r"type Props\s*=\s*\(\s*([\s\S]+?)\)\s*=>\s*([^\n]+)?")
    match = regex.search(type_string)

    if match:
        props = match.group(1).strip()
        output = match.group(2).strip() if match.group(2) else "any"
        return {"props": props or "", "output": output.replace(";", "")}

    return {**DEFAULT_OUTPUT}


def parse_type(type_string):
    regex = re.compile(r"type Props\s*=\s*(?:{[\s\S]+?}|(\([\s\S]+?\)\s*=>\s*[^\n]+))")
    match = regex.search(type_string)

    typescript_type = {"props": None, "output": None}

    if match:
        is_function_type = match.group(1) is not None

        if is_function_type:
            typescript_type = parse_type_method(type_string)
        else:
            typescript_type = parse_type_props(type_string)

    return SimpleNamespace(**typescript_type)


def jinja_render(text, **kwargs):
    template = Template(
        text,
        # variable_start_string="<%",
        # variable_end_string="%>",
        # block_start_string="{%",
        # block_end_string="%}",
    )
    return template.render(
        **kwargs,
        json=lambda data: Markup(json.dumps(data)),
        const=lambda name, data: Markup(f"\nconst {name} = {json.dumps(data)}"),
    )


'''
# Example usage:
dict_type = """
type Props = {
  class?: string | string[] | object;
  style?: string | string[] | object;
  children?: any;
};
"""

method_type = """
type Props = (
    class?: string | string[] | object;
    style?: string | string[] | object;
    children?: any;
) => any;
"""

out_dict = parse_type(dict_type)
out_method = parse_type(method_type)

print(out_dict.get("props"))
print(out_method.get("props"))
'''
