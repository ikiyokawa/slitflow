# -- Project information ------------------------------------------------------

project = 'Slitflow'
copyright = '2022-2023, Yuma Ito'
author = 'Yuma Ito'

release = '0.1'
version = '0.1.0'

# -- General configuration ----------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    'sphinx.ext.autosectionlabel'
]

# -- Options for autodoc ------------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'skimage': ('https://scikit-image.org/docs/stable/', None),
    }

intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output --------------------------------------------------

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output --------------------------------------------------
epub_show_urls = 'footnote'