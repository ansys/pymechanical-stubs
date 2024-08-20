PyMechanical Stubs
==================
|pyansys| |python| |pypi| |downloads| |GH-CI| |codecov| |MIT| |black| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-mechanical-stubs?logo=pypi
   :target: https://pypi.org/project/ansys-mechanical-stubs/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-mechanical-stubs.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-mechanical-stubs
   :alt: PyPI

.. |downloads| image:: https://img.shields.io/pypi/dm/ansys-mechanical-stubs.svg
   :target: https://pypi.org/project/ansys-mechanical-stubs/
   :alt: PyPI Downloads

.. |codecov| image:: https://codecov.io/gh/ansys/pymechanical-stubs/graph/badge.svg?token=UZIC7XT5WE
   :target: https://codecov.io/gh/ansys/pymechanical-stubs
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/pymechanical-stubs/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pymechanical-stubs/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/blog/license/mit
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pymechanical-stubs/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pymechanical-stubs/main
   :alt: pre-commit.ci

.. contents::

Overview
--------

PyMechanical Stubs generates ``__init__.py`` files from assembly files in the Mechanical
application to create python files that can be used for autocomplete with PyMechanical.
Stubs are generated for each version of Mechanical, starting with 2024 R1.

``clr-stubs`` generate Python stubs for .NET assemblies using pythonnet. These stubs are intended
to be used by the autocomplete engine of editors like Atom, Sublime, and VS Code, as well as
for python documentation generation (for example, with Sphinx)

Why clr-stubs?
^^^^^^^^^^^^^^

If you are writing python code using .NET modules via pythonnet's `clr.AddReference`, your IDE's
autocomplete (which usually runs python) will not be able to follow any .NET namespaces or libraries.

The workaround in clr-stubs is to create 'stubs' or 'fakes' with the same namespaces, types, and metadata
that would typically be available in a pure python library. The 'stubs' can then be used by your IDE's
autocomplete.

Manually create ``__init__.py`` files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Install Mechanical 2024 R1.

   **Note**

       Ensure the environment variable, AWP_ROOTDV_DEV, is set to the location of
       Mechanical 2024 R1 (``C:\Program Files\Ansys Inc\v241``).

2. Clone the repository.

   .. code:: bash

        git clone https://github.com/ansys/pymechanical-stubs.git


3. Run stub_generator/create_files.py to generate the stubs from Mechanical 2024 R1.

   .. code:: bash

       python stub_generator/create_files.py

   **Note**

       There may be an Unhandled Exception when the stubs are done running.
       If the message, "Done creating all Mechanical stubs" appears, proceed
       to the next step.

4. Next, create and activate a virtual environment:

   .. code:: bash

       python -m venv .venv

   Windows:

   .. code:: bash

       .venv\Scripts\activate.bat

   Linux:

   .. code:: bash

       source .venv/bin/activate

5. Install ansys-mechanical-stubs

   .. code:: bash

       pip install -e .

6. Make the Sphinx documentation

   .. code:: bash

       make -C doc html

   **Note**

       You can ignore any current warning messages. It is a lengthy process to generate the documentation.

Installation
^^^^^^^^^^^^

You can use `pip <https://pypi.org/project/pip/>`_ to install PyMechanical Stubs.

.. code:: bash

    pip install ansys-mechanical-stubs

To install the latest development version, run these commands:

.. code:: bash

   git clone https://github.com/ansys/pymechanical-stubs
   cd pymechanical-stubs
   pip install -e .

Install in offline mode
^^^^^^^^^^^^^^^^^^^^^^^

If you lack an internet connection or you do not have access to the private Ansys PyPI packages repository,
you should install PyMechanical Stubs by downloading the wheelhouse archive for your corresponding machine
architecture from the repository's `Releases page <https://github.com/ansys/pymechanical-stubs/releases>`_.

Each wheelhouse archive contains all of the Python wheels necessary to install PyMechanical Stubs from scratch on Windows,
Linux, and MacOS from Python 3.10 to 3.12. In addition, you can install the wheelhouse on a new virtual environment
that does not include any previously installed dependencies.

For example, on Linux with Python 3.10, unzip the wheelhouse archive and install it with these commands:

.. code:: bash

    unzip ansys-mechanical-stubs-v0.1.0-wheelhouse-ubuntu-latest-3.10 -d wheelhouse
    pip install ansys-mechanical-stubs -f wheelhouse --no-index --upgrade --ignore-installed

If you are on Windows with Python 3.10, unzip the wheelhouse archive to a wheelhouse directory
and then install using the same ``pip install`` command as in the preceding example.

**Note**

    If desired, you can install the wheelhouse on an isolated  or virtual system.
    See `Creation of virtual environments <https://docs.python.org/3/library/venv.html>`_ in the
    Python documentation for the required steps.

Basic usage
^^^^^^^^^^^

This code shows how to import PyMechanical Stubs and its basic capabilities:

.. code:: python

   from typing import TYPE_CHECKING
   import ansys.mechanical.core as mech

   if TYPE_CHECKING:
       import ansys.mechanical.stubs.v241.Ansys as Ansys

   geometry_import = Model.GeometryImportGroup.AddGeometryImport()

   # Lines that start with "Ansys." will autocomplete as you type
   geometry_import_format = (
       Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
   )
   geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()

Documentation and issues
^^^^^^^^^^^^^^^^^^^^^^^^

Documentation for the latest stable release of PyMechanical Stubs is hosted at `PyMechanical Stubs documentation`_.

In the upper right corner of the documentation's title bar, there is an option for switching from
viewing the documentation for the latest stable release to viewing the documentation for the
development version or previously released versions.

On the `PyMechanical Stubs Issues <https://github.com/ansys/pymechanical-stubs/issues>`_ page,
you can create issues to report bugs and request new features. On the `PyMechanical Stubs Discussions
<https://github.com/ansys/pymechanical-stubs/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <mailto:pyansys.core@ansys.com>`_.

Credits
^^^^^^^

This project is inspired by [ironpython-stubs](https://github.com/gtalarico/ironpython-stubs) but is developed
from scratch.

.. LINKS AND REFERENCES
.. _PyMechanical Stubs documentation: https://scripting.mechanical.docs.pyansys.com/version/stable/index.html
