"""Sphinx documentation configuration file."""

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

from datetime import datetime
import os

from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black

from ansys.mechanical.stubs import __version__

# -- Project information -----------------------------------------------------

project = "ansys.mechanical.stubs"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", default="scripting.mechanical.docs.pyansys.com")


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# -- General configuration ---------------------------------------------------
# Sphinx extensions
extensions = [
    "ansys_sphinx_theme.extension.autoapi",
    "jupyter_sphinx",
    "notfound.extension",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "pypim": ("https://pypim.docs.pyansys.com/version/dev/", None),
}

suppress_warnings = ["label.*", "autoapi.python_import_resolution", "design.grid", "config.cache"]
# supress_warnings = ["ref.option"]


# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    # "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

numpydoc_validation_exclude = {  # set of regex
    # grpc files
    r"\.*pb2\.*",
}

# Favicon
html_favicon = ansys_favicon

# static path
templates_path = ["_templates"]
# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "links.rst",
]

# Copy button customization ---------------------------------------------------
# exclude traditional Python prompts from the copied code
copybutton_prompt_text = r">>> ?|\.\.\. "
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------
html_short_title = html_title = "PyMechanical Stubs"
html_theme = "ansys_sphinx_theme"
html_logo = pyansys_logo_black
html_context = {
    "github_user": "pyansys",
    "github_repo": "pymechanical-stubs",
    "github_version": "main",
    "doc_path": "doc/source",
}
html_theme_options = {
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(version),
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/pymechanical-stubs",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "header_links_before_dropdown": 4,  # number of links before the dropdown menu
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/pymechanical-stubs/discussions",
            "icon": "fa fa-comment fa-fw",
        },
    ],
    "use_meilisearch": {
        "api_key": os.getenv("MEILISEARCH_PUBLIC_API_KEY", ""),
        "index_uids": {
            f"pymechanical-stubs-v{get_version_match(version).replace('.', '-')}": "PyMechanical Stubs",
        },
    },
    "ansys_sphinx_theme_autoapi": {"project": project, "templates": "_templates/autoapi"},
    "navigation_depth": 10,
}

# -- Linkcheck config --------------------------------------------------------

linkcheck_ignore = []

linkcheck_anchors = False

# If we are on a release, we have to ignore the "release" URLs, since it is not
# available until the release is published.
switcher_version = get_version_match(version)
if switcher_version != "dev":
    linkcheck_ignore.append(
        f"https://github.com/ansys/pymechanical-stubs/releases/tag/v{__version__}"
    )
