# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import pathlib
import shutil
import sys

import clr

import stub_generator.generate_content as generate_content

import System  # isort: skip


def get_version():
    """Get the install directory and version of Ansys Mechanical installed on the system.

    Returns
    -------
    str
        Path of the Ansys install set in the AWP_ROOTDV_DEV environment variable.
    int
        The version of the Ansys install set in the AWP_ROOTDV_DEV environment variable.
    """
    install_dir = os.environ["AWP_ROOTDV_DEV"]
    version = int(install_dir[-3:])

    return install_dir, version


def resolve():
    """Add assembly resolver for the Ansys Mechanical install."""
    install_dir, version = get_version()
    platform_string = "winx64" if os.name == "nt" else "linx64"
    sys.path.append(os.path.join(install_dir, "aisol", "bin", platform_string))
    clr.AddReference("Ansys.Mechanical.Embedding")
    import Ansys

    assembly_resolver = Ansys.Mechanical.Embedding.AssemblyResolver
    resolve_handler = assembly_resolver.MechanicalResolveEventHandler
    System.AppDomain.CurrentDomain.AssemblyResolve += resolve_handler


def clean(outdir):
    """Removes src/ansys/mechanical/stubs directory.

    Parameters
    ----------
    outdir: pathlib.Path
        Path to where the init files are generated.
    """
    shutil.rmtree(outdir, ignore_errors=True)


def is_type_published(mod_type: "System.RuntimeType"):
    # TODO - should this filter just get applied by the sphinx system as opposed to the stub generator?
    #        that way all the System stuff we depend on could also get generated (like in the iron-python-stubs
    #        project).
    try:
        attrs = mod_type.GetCustomAttributes(True)
        if len(attrs) == 0:
            return False
        return "Ansys.Utilities.Sdk.PublishedAttribute" in map(str, attrs)
    except Exception as e:
        print(e)


def make(base_dir, outdir, ASSEMBLIES):
    """
    Makes __init__.py files in src/ansys/mechanical/stubs, generates
    classes, properties, and methods with their docstrings from assembly files from the
    Ansys Mechanical install, and adds import statements to the __init__.py files.

    Parameters
    ----------
    outdir: pathlib.Path
        Path to where the init files are generated.
    ASSEMBLIES: list
        List of Mechanical assembly files to create classes, properties, and methods from.
    """
    install_dir, version = get_version()
    version = str(version)
    version = version[:2] + "." + version[2:]
    major_minor = version.split(".")
    major = major_minor[0]
    minor = major_minor[1]

    outdir.mkdir(parents=True, exist_ok=True)

    for assembly in ASSEMBLIES:
        generate_content.make(outdir, assembly, type_filter=is_type_published)

    with open(os.path.join(outdir, "__init__.py"), "w") as f:
        f.write(
            f'''try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata  # type: ignore
patch = importlib_metadata.version("ansys-mechanical-stubs")
"""Patch version for the ansys-mechanical-stubs package."""

# major, minor, patch
version_info = {major}, {minor}, patch
"""Mechanical version with patch version of ansys-mechanical-stubs."""

# Format version
__version__ = ".".join(map(str, version_info))
"""Mechanical Scripting version."""

from .Ansys import *
'''
        )
        f.close()

    path = os.path.join(outdir, "Ansys")

    # Make src/ansys/mechanical/stubs/Ansys/__init__.py
    get_dirs = os.listdir(path)
    with open(os.path.join(path, "__init__.py"), "w") as f:
        # f.write(f'"""The Ansys subpackage containing the Mechanical stubs."""')
        for dir in get_dirs:
            if os.path.isdir(os.path.join(path, dir)):
                f.write(f"import ansys.mechanical.stubs.Ansys.{dir} as {dir}\n")
        f.close()

    # Add import statements to init files
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            full_path = os.path.join(dirpath, dir)
            init_path = os.path.join(full_path, "__init__.py")

            if "__pycache__" not in init_path:
                module_list = []
                import_str = full_path.replace(os.path.join(base_dir, "src", ""), "").replace(
                    os.sep, "."
                )
                [
                    module_list.append(os.path.basename(dir.path))
                    for dir in os.scandir(os.path.dirname(init_path))
                ]

                # Make missing init files
                # if not os.path.isfile(init_path):
                with open(init_path, "a") as f:
                    # Only add docstring if the init file is empty
                    # This is for init files that only contain import statements
                    if os.path.getsize(init_path) == 0:
                        f.write(f'"""{os.path.basename(full_path)} submodule."""\n')
                    for module in module_list:
                        if module != "__init__.py":
                            f.write(f"import {import_str}.{module} as {module}\n")
                    f.close()
    print("Done processing all mechanical stubs.")


def minify():
    pass


def write_docs(commands, tiny_pages_path):
    """Output to the tinypages directory.

    Parameters
    ----------
    tiny_pages_path : str
        Path to the tiny pages directory.

    """

    doc_src = os.path.join(tiny_pages_path, "docs.rst")
    with open(doc_src, "w") as fid:
        fid.write("###################\n")
        fid.write("Autosummary Testing\n")
        fid.write("###################\n")

        fid.write(".. currentmodule:: ansys.mapdl.commands\n\n")
        fid.write(".. autosummary::\n")
        fid.write("   :toctree: _autosummary/\n\n")
        for ans_name in commands:
            cmd_name = ans_name
            fid.write(f"   {cmd_name}\n")


def main():
    MAKE = True
    MINIFY = False
    CLEAN = False

    # Path in which to generate the __init__.py files
    base_dir = pathlib.Path(__file__).parent.parent.parent
    outdir = base_dir / "src" / "ansys" / "mechanical" / "stubs"

    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Assembly files to read from the Ansys Mechanical install.
    ASSEMBLIES = [
        "Ansys.Mechanical.DataModel",
        "Ansys.Mechanical.Interfaces",
        "Ansys.ACT.WB1",
    ]

    resolve()

    if MAKE:
        make(base_dir, outdir, ASSEMBLIES)

    if MINIFY:
        minify()

    if CLEAN:
        clean(outdir)


if __name__ == "__main__":
    main()
