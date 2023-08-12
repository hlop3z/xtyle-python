import os
import pathlib
import sys

import pytest


def dir_up(depth):
    """Easy level-up folder(s)."""
    return sys.path.append(os.path.join(pathlib.Path(__file__).parents[depth], "src"))


# Append to (sys.path)
dir_up(1)


# Testing
from xtyle import JSX

# Root Path
BASE_DIR = pathlib.Path(__file__).parent

# Init Controller
JSX.init(
    base=BASE_DIR,
    # static=BASE_DIR / "static",
    # templates=BASE_DIR / "templates" / "components",
)

# Test One
JSX.component("hello-world")

# Print
print(JSX.dev())

print(JSX.get_config())

JSX.api("create", "button")
JSX.api("delete", "button")

JSX.save()
