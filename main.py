import logging
import os
import pathlib
import shutil
import sys

import clr

import gen

import System  # isort: skip


def get_version():
    install_dir = os.environ["AWP_ROOTDV_DEV"]
    version = int(install_dir[-3:])

    return install_dir, version


def resolve():
    install_dir, version = get_version()
    platform_string = "winx64" if os.name == "nt" else "linx64"
    sys.path.append(os.path.join(install_dir, "aisol", "bin", platform_string))
    clr.AddReference("Ansys.Mechanical.Embedding")
    import Ansys

    assembly_resolver = Ansys.Mechanical.Embedding.AssemblyResolver
    resolve_handler = assembly_resolver.MechanicalResolveEventHandler
    System.AppDomain.CurrentDomain.AssemblyResolve += resolve_handler


resolve()

outdir = pathlib.Path(__file__).parent / "package" / "src" / "ansys" / "mechanical" / "stubs"

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

ASSEMBLIES = [
    "Ansys.Mechanical.DataModel",
    "Ansys.Mechanical.Interfaces",
    "Ansys.ACT.WB1",
]


def clean():
    shutil.rmtree(outdir, ignore_errors=True)


def is_type_published(mod_type: "System.RuntimeType"):
    # TODO - should this filter just get applied by the sphinx system as opposed to the stub generator?
    #        that way all the System stuff we depend on could also get generated (like in the iron-python-stubs
    #        project).
    attrs = mod_type.GetCustomAttributes(True)
    if len(attrs) == 0:
        return False
    return "Ansys.Utilities.Sdk.PublishedAttribute" in map(str, attrs)


def make():
    install_dir, version = get_version()
    version = str(version)
    version = version[:2] + "." + version[2:]
    major_minor = version.split(".")
    major = major_minor[0]
    minor = major_minor[1]

    outdir.mkdir(parents=True, exist_ok=True)

    for assembly in ASSEMBLIES:
        gen.make(outdir, assembly, type_filter=is_type_published)

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

    path = os.path.join("package", "src", "ansys", "mechanical", "stubs", "Ansys")

    # Make src/ansys/mechanical/stubs/Ansys/__init__.py
    get_dirs = os.listdir(path)
    with open(os.path.join(path, "__init__.py"), "w") as f:
        # f.write(f'"""The Ansys subpackage containing the Mechanical stubs."""')
        for dir in get_dirs:
            if os.path.isdir(os.path.join(path, dir)):
                f.write(f"import ansys.mechanical.stubs.Ansys.{dir} as {dir}\n")
        f.close()

    # Add import statements to init files
    for (dirpath, dirnames, filenames) in os.walk(path):
        for dir in dirnames:
            full_path = os.path.join(dirpath, dir)
            init_path = os.path.join(full_path, '__init__.py')

            if "__pycache__" not in init_path:
                module_list = []
                import_str = full_path.replace(os.sep, '.').replace("package.src.", '')
                [ module_list.append(os.path.basename(dir.path)) for dir in os.scandir(os.path.dirname(init_path)) ]

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


# TODO - argparse
MAKE = True
MINIFY = False
CLEAN = False
if CLEAN:
    clean()

if MAKE:
    make()

if MINIFY:
    minify()


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
