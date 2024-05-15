# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import datetime
import os
from pathlib import Path

from ansys.mechanical.stubs import __version__
from ansys_sphinx_theme import (
    ansys_favicon,
    get_autoapi_templates_dir_relative_path,
    get_version_match,
    pyansys_logo_black,
)
from sphinx.builders.latex import LaTeXBuilder

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Project information
project = "ansys-mechanical-scripting"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", default="scripting.mechanical.docs.pyansys.com")
switcher_version = get_version_match(__version__)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Sphinx extensions
extensions = [
    "autoapi.extension",
    "numpydoc",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_markdown_builder",
]

markdown_anchor_sections = True
markdown_anchor_signatures = True

exclude_patterns = ["_autoapi_templates", "_build", "Thumbs.db", ".DS_Store"]

# Configuration for Sphinx autoapi
autoapi_type = "python"
autoapi_dirs = ["../../src/ansys"]
autoapi_root = "api"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
]
autoapi_template_dir = get_autoapi_templates_dir_relative_path(Path(__file__))
suppress_warnings = ["autoapi.python_import_resolution"]
autoapi_python_use_implicit_namespaces = True
autoapi_keep_files = True
autoapi_render_in_single_page = ["class", "enum", "exception"]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "imageio": ("https://imageio.readthedocs.io/en/stable", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
}

# Numpydoc config
numpydoc_use_plots = True
numpydoc_show_class_members = False  # we take care of autosummary on our own
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    # general
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    # "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    # Summary
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    "SS03",  # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    "SS05",  # Summary must start with infinitive verb, not third person
    # Parameters
    "PR10",  # Parameter "{param_name}" requires a space before the colon '
    # separating the parameter name and type",
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Favicon
html_favicon = ansys_favicon

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "api/ansys/mechanical/stubs/index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# The language for content autogenerated by Sphinx_PyAEDT. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "Mechanical API Documentation"

# specify the location of your github repo
html_context = {
    "github_user": "ansys",
    "github_repo": "mechanical-stubs",
    "github_version": "main",
    "doc_path": "doc/source",
}
html_theme_options = {
    "navigation_depth": 10,
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/mechanical-stubs",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyMechanical", "https://mechanical.docs.pyansys.com/"),
        (
            "Mechanical Scripting",
            "https://mechanical.docs.pyansys.com/version/stable/user_guide_scripting/index.html",
        ),
    ],
}