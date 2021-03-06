# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_rtd_theme
from datetime import date

sys.path.insert(0, os.path.abspath('../'))

from easyInterface.Utils.Helpers import getReleaseInfo
project_info = getReleaseInfo(os.path.join('..', 'easyInterface', 'Release.json'))

# -- Project information -----------------------------------------------------

project = project_info['name']
copyright = '2019-{}, {}'.format(date.today().year, project_info['author'])
author = project_info['author']

# The full version, including alpha/beta/rc tags

release = project_info['version']


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_gallery.gen_gallery',
]

sphinx_gallery_conf = {
    'examples_dirs': '../examples',   # path to your example scripts
    'gallery_dirs': 'auto_examples',  # path to where to save gallery generated output
    'binder': {'org': 'easyDiffraction',
               'repo': 'easyInterface',
               'branch': 'gh-pages',
               'binderhub_url': 'https://mybinder.org',
               'dependencies': './requirements.txt',
               'notebooks_dir': 'tutorials',
               'use_jupyter_lab': True,
               },
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

source_suffix = ['.rst', '.md']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# The theme is set by the make target
html_theme = os.environ.get('SPHX_GLR_THEME', 'rtd')

# on_rtd is whether we are on readthedocs.org, this line of code grabbed
# from docs.readthedocs.org
if html_theme == 'rtd':
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


def setup(app):
    """Sphinx setup function."""
    app.add_css_file('theme_override.css')

html_theme_options = {
    'display_version': True
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

master_doc = 'index'

pygments_style = 'sphinx'
highlight_language = 'python3'

html_show_sourcelink = False

# html_logo = '_static/logo.png'