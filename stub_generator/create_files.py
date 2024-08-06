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
"""Create __init__.py files from the content of the assembly XML files."""

import logging
import os
import pathlib
import shutil
import sys

import clr
import generate_content

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
    sys.path.append(install_dir / "aisol" / "bin" / platform_string)
    clr.AddReference("Ansys.Mechanical.Embedding")
    import Ansys

    assembly_resolver = Ansys.Mechanical.Embedding.AssemblyResolver
    resolve_handler = assembly_resolver.MechanicalResolveEventHandler
    System.AppDomain.CurrentDomain.AssemblyResolve += resolve_handler


def clean(outdir):
    """Remove src/ansys/mechanical/stubs directory.

    Parameters
    ----------
    outdir: pathlib.Path
        Path to where the init files are generated.
    """
    shutil.rmtree(outdir, ignore_errors=True)


def is_type_published(mod_type: "System.RuntimeType"):
    """Get published type if it exists.

    Parameters
    ----------
    mod_type: System.RuntimeType
        A module type.

    Returns
    -------
    bool
        `True` if "Ansys.Utilities.Sdk.PublishedAttribute" is in map(str, attrs)
        `False` if "Ansys.Utilities.Sdk.PublishedAttribute" is not in map(str, attrs)
    """
    try:
        attrs = mod_type.GetCustomAttributes(True)
        if len(attrs) == 0:
            return False
        return "Ansys.Utilities.Sdk.PublishedAttribute" in map(str, attrs)
    except Exception as e:
        print(e)


def make(base_dir, outdir, assemblies, str_version):
    """Generate the __init__.py files from assembly files.

    Make __init__.py files in src/ansys/mechanical/stubs, generate
    classes, properties, and methods with their docstrings from assembly files from the
    Ansys Mechanical install, and add import statements to the __init__.py files.

    Parameters
    ----------
    outdir: pathlib.Path
        Path to where the init files are generated.
    assemblies: list
        List of Mechanical assembly files to create classes, properties, and methods from.
    """
    install_dir, version = get_version()
    version = str(version)
    version = version[:2] + "." + version[2:]

    outdir.mkdir(parents=True, exist_ok=True)

    for assembly in assemblies:
        generate_content.make(outdir, assembly, type_filter=is_type_published)

    with pathlib.Path.open(outdir / "__init__.py", "w") as f:
        f.write(f'"""Ansys Mechanical {str_version} subpackage."""\n')
        f.write(f"""import ansys.mechanical.stubs.{str_version}.Ansys as Ansys""")

    path = outdir / "Ansys"

    # Make src/ansys/mechanical/stubs/v241/Ansys/__init__.py
    get_dirs = os.listdir(path)
    with pathlib.Path.open(path / "__init__.py", "w") as f:
        f.write('"""Ansys subpackage."""\n')
        for dir in get_dirs:
            if pathlib.Path.is_dir(path / dir):
                f.write(f"import ansys.mechanical.stubs.{str_version}.Ansys.{dir} as {dir}\n")
        f.close()

    # Add import statements to init files
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            full_path = dirpath / dir
            init_path = full_path / "__init__.py"

            if "__pycache__" not in init_path:
                module_list = []
                import_str = full_path.replace(base_dir / "src" / "", "").replace(os.sep, ".")
                [
                    module_list.append(pathlib.Path(dir.path).name)
                    for dir in os.scandir(pathlib.Path(init_path).parent)
                ]

                # Make missing init files
                # if not os.path.isfile(init_path):
                with pathlib.Path.open(init_path, "a") as f:
                    # Only add docstring if the init file is empty
                    # This is for init files that only contain import statements
                    if pathlib.Path.stat(init_path).st_size == 0:
                        f.write(f'"""{pathlib.Path(full_path).name} submodule."""\n')
                    for module in module_list:
                        if module != "__init__.py":
                            f.write(f"import {import_str}.{module} as {module}\n")
                    f.close()
    print("Done processing all mechanical stubs.")


def write_docs(commands, tiny_pages_path):
    """Output to the tinypages directory.

    Parameters
    ----------
    tiny_pages_path : str
        Path to the tiny pages directory.
    """
    doc_src = pathlib.Path(tiny_pages_path / "docs.rst")
    with pathlib.Path.open(doc_src, "w") as fid:
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
    """Generate the Mechanical stubs based on assembly files."""
    make_bool = True
    clean_bool = False

    # Get version of the Mechanical install
    install_dir, version = get_version()
    version = f"v{str(version)}"

    # Path in which to generate the __init__.py files
    base_dir = pathlib.Path(__file__).parent.parent
    outdir = base_dir / "src" / "ansys" / "mechanical" / "stubs" / version

    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Assembly files to read from the Ansys Mechanical install.
    assemblies = [
        "Ansys.Mechanical.DataModel",
        "Ansys.Mechanical.Interfaces",
        "Ansys.ACT.WB1",
    ]

    resolve()

    if make_bool:
        make(base_dir, outdir, assemblies, version)

    if clean_bool:
        clean(outdir)


if __name__ == "__main__":
    main()
