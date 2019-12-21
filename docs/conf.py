#!/usr/bin/env python

import sprockets_logging

needs_sphinx = '1.0'
extensions = []
templates_path = []
source_suffix = '.rst'
master_doc = 'index'
project = 'sprockets_logging'
author = 'Dave Shawley'
copyright = '2019, AWeber Communications'
version = '.'.join(str(c) for c in sprockets_logging.version_info[:2])
release = sprockets_logging.version
html_static_path = ['.']
need_sphinx = '2.0'

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
extensions.append('sphinx.ext.autodoc')

# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
extensions.append('sphinx.ext.intersphinx')
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'tornado': ('https://www.tornadoweb.org/en/stable/', None),
}

# https://sphinxcontrib-httpdomain.readthedocs.io/en/stable/
extensions.append('sphinxcontrib.httpdomain')
