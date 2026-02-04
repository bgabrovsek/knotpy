# Configuration file for the Sphinx documentation builder.
# 
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------
project = 'KnotPy'
copyright = '2025, Boštjan Gabrovšek'
author = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'


# -- General configuration ---------------------------------------------------


extensions = [
    "myst_nb",
    #"myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
]


source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    #".md": "markdown",
}

nb_execution_mode = "cache"
nb_execution_timeout = 120
nb_execution_mode = "off"

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**/.ipynb_checkpoints']

# -- Docstring style & autosummary -------------------------------------------------
autosummary_generate = True
autosummary_generate_overwrite = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = False
autodoc_typehints = "description"

autodoc_default_options = {
    "members": True,
    "undoc-members": True,         # show even functions without docstrings
    "show-inheritance": False,
    # If __all__ is hiding things, uncomment the next line:
    # "ignore-module-all": True,
}
autodoc_member_order = "bysource"  # optional: keep source order

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# -- Options for HTML output -------------------------------------------------
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'navigation_with_keys': False,
    'show_prev_next': False,
    "secondary_sidebar_items": ["page-toc"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/bgabrovsek/knotpy",
            "icon": "fab fa-github",
        },
    ],
}

html_sidebars = {
    "**": ["sidebar-nav-bs"],
    "index": [],
    "install": [],
    "tutorial/**": [],
}

html_sidebars.update({
    "examples/**": [],
})


html_logo = "_static/logo.png"
# html_favicon = "_static/logo.ico"

html_copy_source = False

html_static_path = ["_static"]

# TODO: Configure latex output