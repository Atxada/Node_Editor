# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
import GUI

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'NodeEditor'
copyright = '2024, Aldo Aldrich'
author = 'Aldo Aldrich'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'recommonmark', #for enabling markdown
]   

autosectionlabel_prefix_document = True

autodoc_member_order = "bysource"
autoclass_content = "both"    # force sphinx to show parameter of constructor under each class

from recommonmark.transform import AutoStructify
github_doc_root = 'https://github.com/rtfd/recommonmark/tree/master/doc/'
def setup(app):
    app.add_config_value('recommonmark_config', {
            # 'url_resolver': lambda url: github_doc_root + url,
            'auto_toc_tree_section': 'Contents',
            }, True)
    app.add_transform(AutoStructify)

templates_path = ['_templates']

source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'    # [classic / alabaster]
html_theme_path = ["_themes", ]
html_static_path = ['_static']

htmlhelp_basename = 'NodeEditordoc'
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'NodeEditor.tex', 'NodeEditor Documentation',
     'Pavel Křupala', 'manual'),
]

man_pages = [
    (master_doc, 'nodeeditor', 'NodeEditor Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'NodeEditor', 'NodeEditor Documentation',
     author, 'NodeEditor', 'One line description of project.',
     'Miscellaneous'),
]

epub_title = project

epub_exclude_files = ['search.html']
