import clr
import System  # isort: skip
import logging
import os
import pathlib
import shutil
import sys

import gen

def resolve():
    install_dir = os.environ["AWP_ROOTDV_DEV"]
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

outdir = pathlib.Path(__file__).parent / "out"
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
    outdir.mkdir(exist_ok=True)
    for assembly in ASSEMBLIES:
        gen.make(outdir, assembly, type_filter=is_type_published)

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