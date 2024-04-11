# Configuration file for the Sphinx documentation builder.
# 
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------
project = 'KnotPy'
copyright = '2024, Boštjan Gabrovšek'
author = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx_gallery.gen_gallery',
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
    "secondary_sidebar_items": ["page-toc"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/bgabrovsek/knotpy",
            "icon": "fab fa-github",
        },
    ],
}

# Don't show sidebar on the index, installation and tutorial pages.
html_sidebars = {
    "**": ["sidebar-nav-bs"],
    "index": [],
    "install": [],
    "tutorial": [],
}

sphinx_gallery_conf = {
    'examples_dirs': '../examples',
    'gallery_dirs': 'auto_examples',
    'image_scrapers': ('matplotlib',),
    'matplotlib_animations': True,
}

html_logo = "_static/logo.png"
# html_favicon = "_static/logo.ico"

html_copy_source = False

html_static_path = ["_static"]

# TODO: Configure latex output