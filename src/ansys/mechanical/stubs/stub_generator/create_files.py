# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path
import shutil
import sys

import clr
import generate_content

import System  # isort: skip

ACCEPTED_TYPES = {
    "Ansys.Core.Units.Quantity",
    "Ansys.ACT.Interfaces.Common",
    "Ansys.Mechanical.DataModel.Interfaces.IDataModelObject",
}


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
    ansys_mech_embedding_path = str(Path(install_dir, "aisol", "bin", platform_string))

    # Append path for Ansys.Mechanical.Embedding
    sys.path.append(ansys_mech_embedding_path)
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
            try:
                if mod_type.FullName in ACCEPTED_TYPES:
                    return True
            except:  # noqa: E722
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

    outdir_init = outdir / "__init__.py"
    with outdir_init.open("w") as f:
        f.write(f'"""Ansys Mechanical {str_version} module."""\n')
        f.write(f"""import ansys.mechanical.stubs.{str_version}.Ansys as Ansys""")

    path = outdir / "Ansys"
    path_init = path / "__init__.py"

    # Make src/ansys/mechanical/stubs/v241/Ansys/__init__.py
    with path_init.open("w") as f:
        f.write('"""Ansys module."""\n')
        for directory in path.iterdir():
            if directory.is_dir():
                dir_name = directory.name
                f.write(
                    f"import ansys.mechanical.stubs.{str_version}.Ansys.{dir_name} as {dir_name}\n"
                )
        f.close()

    # Add import statements to init files
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            full_path = str(Path(dirpath, dir))
            init_path = Path(full_path, "__init__.py")

            if "__pycache__" not in str(init_path):
                module_list = []
                original_str = f"{Path(base_dir)}{os.sep}"
                import_str = full_path.replace(original_str, "ansys.mechanical.stubs.").replace(
                    os.sep, "."
                )
                [
                    module_list.append(Path(dir.path).name)
                    for dir in os.scandir(Path(init_path).parent)
                ]

                # Create list of import statements for each submodule. For example,
                # "import ansys.mechanical.stubs.v241.Ansys.ACT.Common as Common"
                # in Ansys/ACT/__init__.py
                import_statements = []
                for module in module_list:
                    if module != "__init__.py":
                        import_statements.append(f"import {import_str}.{module} as {module}\n")

                # If __init__ file is empty, add a docstring to the top of the file and
                # write module import statements. For example, Ansys/ACT/__init__.py
                if (not init_path.is_file()) or (init_path.stat().st_size == 0):
                    with init_path.open("a") as f:
                        f.write(f'"""{Path(full_path).name} module."""\n')
                        f.write("".join(import_statements))
                else:
                    # Add "import Ansys" to the top of __init__ files
                    import_statements.insert(0, "if typing.TYPE_CHECKING:\n    import Ansys\n")

                    # Read the __init__ file contents
                    with init_path.open("r", encoding="utf-8") as f:
                        content_list = f.readlines()
                        if '"' in content_list[0]:
                            content_list.insert(1, "from __future__ import annotations\n")
                        else:
                            content_list.insert(0, "from __future__ import annotations\n")
                        contents = "".join(content_list)

                    # Add all module import statements from import_statements to the top of the file
                    # For example, Ansys/ACT/Automation/Mechanical
                    with init_path.open("w", encoding="utf-8") as f:
                        contents = contents.replace(
                            "import typing", f"import typing\n{''.join(import_statements)}"
                        )

                        f.write(contents)

                        datamodel_interfaces = (
                            Path("Ansys") / "Mechanical" / "DataModel" / "Interfaces"
                        )
                        if str(datamodel_interfaces) in str(init_path):
                            f.write("class DataModelObject(IDataModelObject):\n")
                            f.write("    pass\n")

    print("Done processing all mechanical stubs.")


def write_docs(commands, tiny_pages_path):
    """Output to the tinypages directory.

    Parameters
    ----------
    tiny_pages_path : str
        Path to the tiny pages directory.
    """
    doc_src = Path(tiny_pages_path / "docs.rst")
    with doc_src.open("w") as fid:
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
    base_dir = Path(__file__).parent.parent
    outdir = base_dir / version

    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Assembly files to read from the Ansys Mechanical install.
    assemblies = [
        # "Ansys.Mechanical.DataModel",
        # "Ansys.Mechanical.Interfaces",
        # "Ansys.ACT.Interfaces",
        # "Ansys.ACT.WB1",
        "Ans.Core",
    ]

    resolve()

    if make_bool:
        make(base_dir, outdir, assemblies, version)

    if clean_bool:
        clean(outdir)


if __name__ == "__main__":
    main()
