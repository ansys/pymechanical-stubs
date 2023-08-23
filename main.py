import clr
import System  # isort: skip
import logging
import os
import pathlib
import shutil
import sys

import gen

def resolve():
    install_dir = os.environ["AWP_ROOT232"] # Change this back to AWP_ROOTDV_DEV
    platform_string = "winx64" if os.name == "nt" else "linx64"
    sys.path.append(os.path.join(install_dir, "aisol", "bin", platform_string))
    version = int(install_dir[-3:])
    clr.AddReference("Ansys.Mechanical.Embedding")
    import Ansys
    assembly_resolver = Ansys.Mechanical.Embedding.AssemblyResolver
    if version == 231:
        resolve_handler = assembly_resolver.WindowsResolveEventHandler
    else:
        resolve_handler = assembly_resolver.MechanicalResolveEventHandler
    System.AppDomain.CurrentDomain.AssemblyResolve += resolve_handler

resolve()

outdir = pathlib.Path(__file__).parent / "package" / "src" 
logging.getLogger().setLevel(logging.INFO)

ASSEMBLIES = [
    "Ansys.Mechanical.DataModel",
    "Ansys.Mechanical.Interfaces",
    "Ansys.ACT.WB1"
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
    outdir.mkdir(parents=True, exist_ok=True)    
    for assembly in ASSEMBLIES:
        gen.make(outdir, assembly, type_filter=is_type_published)
    
    with open(os.path.join(outdir, "Ansys","__init__.py"), 'w') as f:
        f.write('''try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata  # type: ignore
__version__ = importlib_metadata.version("ansys-mechanical-stubs")
"""Mechanical Scripting version"""
''')
        
    print("Done creating all Mechanical stubs.")


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