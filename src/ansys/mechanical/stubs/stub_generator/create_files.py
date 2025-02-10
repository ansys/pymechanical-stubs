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

import argparse
import logging
import os
import pathlib
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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.
    """
    # Set argparser
    argparser = argparse.ArgumentParser(description="Generate Mechanical stubs.")

    # Arguments for generating stubs
    argparser.add_argument("--make", action="store_true", help="Generate stubs.")
    argparser.add_argument("--clean", action="store_true", help="Clean stubs.")

    # Show logging.DEBUG statements
    argparser.add_argument("--debug", action="store_true", help="Print logging.debug() statements.")

    # Arguments for assemblies to generate stubs for
    argparser.add_argument(
        "--all-assemblies", action="store_true", help="Make stubs for all assemblies."
    )
    argparser.add_argument(
        "--mechanical-datamodel",
        action="store_true",
        help="Make stubs for Ansys.Mechanical.DataModel.",
    )
    argparser.add_argument(
        "--mechanical-interfaces",
        action="store_true",
        help="Make stubs for Ansys.Mechanical.Interfaces.",
    )
    argparser.add_argument(
        "--act-interfaces", action="store_true", help="Make stubs for Ansys.ACT.Interfaces."
    )
    argparser.add_argument("--act-wb1", action="store_true", help="Make stubs for Ansys.ACT.WB1.")
    argparser.add_argument("--ans-core", action="store_true", help="Make stubs for Ans.Core.")

    # Version of the Mechanical install to create stubs for
    argparser.add_argument("--version", type=str, help="Version of the Mechanical install.")

    return argparser.parse_args()


def get_mech_install_info(version: str) -> tuple:
    """Get the Mechanical install directory and version if not provided.

    Parameters
    ----------
    version : str | None
        Version of the Mechanical install.

    Returns
    -------
    install_dir : str
        The Mechanical install directory.
    v_version : str
        Version of the Mechanical install with v. For example, v251.
    """
    if not version:
        install_dir = os.environ["AWP_ROOTDV_DEV"]
        version = int(install_dir[-3:])
    else:
        install_dir = os.environ[f"AWP_ROOT{version}"]

    return install_dir, f"v{version}"


def make_assemblies_list(args: argparse.Namespace) -> list:
    """Make a list of assemblies to generate stubs for.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments.

    Returns
    -------
    list
        List of assemblies to generate stubs for.
    """
    assemblies = []
    if args.all_assemblies:
        assemblies = [
            "Ansys.Mechanical.DataModel",
            "Ansys.Mechanical.Interfaces",
            "Ansys.ACT.Interfaces",
            "Ansys.ACT.WB1",
            "Ans.Core",
        ]
    else:
        if args.mechanical_datamodel:
            assemblies.append("Ansys.Mechanical.DataModel")
        if args.mechanical_interfaces:
            assemblies.append("Ansys.Mechanical.Interfaces")
        if args.act_interfaces:
            assemblies.append("Ansys.ACT.Interfaces")
        if args.act_wb1:
            assemblies.append("Ansys.ACT.WB1")
        if args.ans_core:
            assemblies.append("Ans.Core")

    return assemblies


def resolve(install_dir):
    """Add assembly resolver for the Ansys Mechanical install."""
    platform_string = "winx64" if os.name == "nt" else "linx64"
    ansys_mech_embedding_path = str(pathlib.Path(install_dir, "aisol", "bin", platform_string))

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
    outdir.mkdir(parents=True, exist_ok=True)

    for assembly in assemblies:
        generate_content.make(outdir, assembly, type_filter=is_type_published)

    outdir_init = outdir / "__init__.py"
    with pathlib.Path.open(outdir_init, "w") as f:
        f.write(f'"""Ansys Mechanical {str_version} module."""\n')
        f.write(f"""import ansys.mechanical.stubs.{str_version}.Ansys as Ansys""")

    path = outdir / "Ansys"
    path_init = path / "__init__.py"

    # Make src/ansys/mechanical/stubs/v241/Ansys/__init__.py
    get_dirs = os.listdir(path)
    with pathlib.Path.open(path_init, "w") as f:
        f.write('"""Ansys module."""\n')
        for dir in get_dirs:
            full_dir_path = path / dir
            if pathlib.Path.is_dir(full_dir_path):
                f.write(f"import ansys.mechanical.stubs.{str_version}.Ansys.{dir} as {dir}\n")
        f.close()

    # Add import statements to init files
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            full_path = str(pathlib.Path(dirpath, dir))
            init_path = pathlib.Path(full_path, "__init__.py")

            if "__pycache__" not in str(init_path):
                module_list = []
                original_str = f"{pathlib.Path(base_dir)}{os.sep}"
                import_str = full_path.replace(original_str, "ansys.mechanical.stubs.").replace(
                    os.sep, "."
                )
                [
                    module_list.append(pathlib.Path(dir.path).name)
                    for dir in os.scandir(pathlib.Path(init_path).parent)
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
                if (not pathlib.Path.is_file(init_path)) or (
                    pathlib.Path.stat(init_path).st_size == 0
                ):
                    with pathlib.Path.open(init_path, "a") as f:
                        f.write(f'"""{pathlib.Path(full_path).name} module."""\n')
                        f.write("".join(import_statements))
                else:
                    # Add "import Ansys" to the top of __init__ files
                    import_statements.insert(0, "if typing.TYPE_CHECKING:\n    import Ansys\n")

                    # Read the __init__ file contents
                    with pathlib.Path.open(init_path, "r", encoding="utf-8") as f:
                        content_list = f.readlines()
                        if '"' in content_list[0]:
                            content_list.insert(1, "from __future__ import annotations\n")
                        else:
                            content_list.insert(0, "from __future__ import annotations\n")
                        contents = "".join(content_list)

                    # Add all module import statements from import_statements to the top of the file
                    # For example, Ansys/ACT/Automation/Mechanical
                    with pathlib.Path.open(init_path, "w", encoding="utf-8") as f:
                        contents = contents.replace(
                            "import typing", f"import typing\n{''.join(import_statements)}"
                        )

                        f.write(contents)

                        datamodel_interfaces = (
                            pathlib.Path("Ansys") / "Mechanical" / "DataModel" / "Interfaces"
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
    # Get command line arguments
    args = parse_args()

    # Get the Mechanical install directory and version (if args.version is not provided)
    install_dir, v_version = get_mech_install_info(args.version)

    # Path in which to generate the __init__.py files
    base_dir = pathlib.Path(__file__).parent.parent
    outdir = base_dir / v_version

    # Set logging level and configuration
    logging.getLogger().setLevel(logging.INFO)
    if args.debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # Assembly files to read from the Ansys Mechanical install
    assemblies = make_assemblies_list(args)

    resolve(install_dir)

    if args.make:
        make(base_dir, outdir, assemblies, v_version)

    if args.clean:
        clean(outdir)


if __name__ == "__main__":
    main()
