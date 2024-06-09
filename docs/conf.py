# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

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
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]   

autodoc_member_order = "bysource"
autoclass_content = "both"    # force sphinx to show parameter of constructor under each class

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'    # [classic / alabaster]
html_theme_path = ["_themes", ]
html_static_path = ['_static']
