# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import importlib
import os
import sys
from datetime import date
from pathlib import Path


sys.path.insert(0, str((Path(__file__).parent.parent / "src").resolve().absolute()))

import tomllib
from pathlib import Path


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

with (Path(__file__).parent.parent / "pyproject.toml").open("rb") as __fh:
    pyproject = tomllib.load(__fh)

project = pyproject["project"]["name"]
author = ", ".join(__x["name"] for __x in pyproject["project"]["authors"])
project_group_name = os.getenv("GITHUB_REPOSITORY_OWNER", "") or author
project_group_name = project_group_name.lower().replace("-", " ").replace("_", " ").title()
copyright = f"{date.today().year}, {project_group_name}"

version = importlib.import_module(project).__version__
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = "friendly"
pygments_dark_style = "native"

html_theme = "sphinx_book_theme"
html_show_sphinx = False
html_static_path = ["_static"]
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.png"
html_css_files = ["custom.css"]

_repo = os.getenv("GITHUB_REPOSITORY", "")

html_theme_options = {
    "home_page_in_toc": True,
    "show_navbar_depth": 4,
    "collapse_navbar": True,
    "repository_provider": "github",
    "repository_branch": "main",
}

if _repo:
    html_theme_options["use_repository_button"] = True
    html_theme_options["repository_url"] = f"https://github.com/{_repo}"

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
autosummary_generate = True
