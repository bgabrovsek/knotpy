# Configuration file for the Sphinx documentation builder.
# 
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------
project = 'knotpy'
copyright = '2023, Boštjan Gabrovšek'
author = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]

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
}

# TODO: Add logo and favicon
# html_logo = "_static/logo.svg"
# html_favicon = "_static/logo.ico"

html_copy_source = False

html_static_path = ['_static']

# TODO: Configure latex output