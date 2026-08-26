# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# This is neeed for autosummary to find the path to the source code
# It is based on using a flat package layout
# https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyaml-cs-oa"
copyright = '2026, pyAML Collaboration'
author = 'pyAML Collaboration'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_title = "pyaml-cs-oa"

html_css_files = [
    "custom.css",
]

html_theme_options = {
    "navigation_depth": 4,
    "show_nav_level": 2,
}

html_sidebars = {
    "**": [
        "sidebar-collapse",
        "sidebar-nav-bs",
    ],
}
