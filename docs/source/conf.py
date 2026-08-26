# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


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
    "sphinx.ext.napoleon",
    "myst_parser",
]

autosummary_generate = True

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_title = "pyaml-cs-oa"
html_show_sourcelink = False
html_css_files = ["custom.css"]
html_logo = "_static/_images/logo.png"

html_theme_options = {
    "navigation_depth": 4,
    "show_nav_level": 2,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/python-accelerator-middle-layer/pyaml-cs-oa",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
}

html_sidebars = {
    "**": [
        "sidebar-collapse",
        "sidebar-nav-bs",
    ],
}