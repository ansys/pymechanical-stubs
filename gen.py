"""Module containing routine to generate python stubs for an assembly."""

import json
import logging
import os
import pathlib
import typing
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import clr
import System


def is_namespace(something):
    """Returns True if object is Namespace: Module"""
    if isinstance(something, type(System)):
        return True


def iter_module(module, type_filter: typing.Callable = None):
    """
    Recursively iterate through all namespaces in assembly
    """
    mod_types = module.GetTypes()
    namespaces = {}
    for mod_type in mod_types:
        if type_filter and not type_filter(mod_type):
            continue
        namespace = mod_type.Namespace
        if namespace not in namespaces.keys():
            namespaces[namespace] = [mod_type]
        else:
            namespaces[namespace].append(mod_type)
    return namespaces


def crawl_loaded_references(assembly, type_filter: typing.Callable = None) -> dict:
    """Crawl Loaded assemblies to get Namespaces."""
    return iter_module(assembly, type_filter)


def dump_types(namespaces):
    printable_namespaces = {k: [x.Name for x in v] for k, v in namespaces.items()}
    logging.debug(json.dumps(printable_namespaces, indent=2, sort_keys=True))


class DocMember:
    """Docstring member."""

    def __init__(self, element: ET.Element):
        self._element = element

    @classmethod
    def __get_element_text(self, element: typing.Optional[ET.Element]):
        if element is None:
            return None
        return element.text

    @property
    def name(self) -> str:
        return self._element.attrib["name"]

    @property
    def summary(self) -> str:
        return self.__get_element_text(self._element.find("summary"))

    @property
    def params(self) -> str:
        return self._element.findall("param")

    @property
    def remarks(self) -> str:
        return self.__get_element_text(self._element.find("remarks"))

    @property
    def example(self) -> ET.Element:
        return self._element.find("example")


def write_docstring(
    buffer: typing.TextIO, doc_member: typing.Optional[DocMember], indent_level=1
) -> None:
    """Write docstring of class or enum with the given indentation level, if available."""
    if doc_member is None:
        return
    summary = doc_member.summary
    if summary is None:
        return
    indent = "    " * indent_level
    buffer.write(f'{indent}"""\n')
    buffer.write(f"{indent}{summary}\n")
    buffer.write(f'{indent}"""\n')


ENUM_VALUE_REPLACEMENTS = {"None": "None_", "True": "True_"}


def write_enum_field(
    buffer: typing.TextIO, field: typing.Any, indent_level: int = 1
) -> None:
    name = field.Name
    logging.debug(f"        writing enum value {name}")
    int_value = field.GetRawConstantValue()
    str_value = ENUM_VALUE_REPLACEMENTS.get(name, name)
    indent = "    " * indent_level
    buffer.write(f"{indent}{str_value} = {int_value}\n")


def write_enum(
    buffer: typing.TextIO,
    enum_type: typing.Any,
    namespace: str,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> None:
    logging.debug(f"    writing enum {enum_type.Name}")
    fields = [
        field
        for field in enum_type.GetFields()
        if field.IsLiteral and (type_filter is None or type_filter(field))
    ]
    buffer.write(f"class {enum_type.Name}(Enum):\n")
    enum_doc = doc.get(f"T:{namespace}.{enum_type.Name}", None)
    write_docstring(buffer, enum_doc, 1)
    buffer.write("\n")
    for field in fields:
        write_enum_field(buffer, field, 1)
    if len(fields) == 0:
        # TODO - some Mechanical types are published but don't have published values, like PinNature. These
        #        should be handled as bugs for the Mechanical team.
        buffer.write("    pass\n")
    buffer.write("\n")


# Helper for fix_str()
def remove_backtick(input_str):
    backtick = input_str.index("`")
    new_str = input_str[0:backtick] + input_str[backtick+2:]

    if "`" in new_str:
        return remove_backtick(new_str)
    else:
        return new_str


# Helper for get_properties() and write_properties
def fix_str(input_str):
    if "+" in input_str:
        input_str = input_str.replace("+", ".")
    if "[]" in input_str:
        input_str = input_str.replace("[]", "")
    if "`" in input_str:
        input_str = remove_backtick(input_str)
    return input_str

@dataclass
class Param:
    type: str
    name: str


@dataclass
class Method:
    name: str
    doc: DocMember
    return_type: str
    static: bool
    args: typing.List[Param]


@dataclass
class Property:
    name: str
    type: str
    getter: bool
    setter: bool
    doc: DocMember
    static: bool
    value: typing.Optional[typing.Any]  # may be used if static


def get_properties(
    class_type: typing.Any,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> typing.List[Property]:
    # TODO - base class properties are not handled here. They might be published if they are ansys types
    #        or not if they are system types (e.g. the IList methods implemented by an Ansys type that derives from System.Collections.Generic.IList)
    props = [
        prop
        for prop in class_type.GetProperties()
        if (type_filter is None or type_filter(prop))
    ]
    output = []
    for prop in props:
        prop_type = f'"{fix_str(prop.PropertyType.ToString())}"'
        prop_name = prop.Name
        declaring_type_name = prop.DeclaringType.ToString()
        method_doc_key = f"P:{declaring_type_name}.{prop_name}"
        prop_doc = doc.get(method_doc_key, None)
        property = Property(
            getter=False,
            setter=False,
            type=prop_type,
            name=prop_name,
            doc=prop_doc,
            static=False,
            value=None,
        )
        get_method = prop.GetMethod
        if get_method:
            if class_type.IsInterface or get_method.IsPublic:
                property.getter = True
            if (
                get_method.IsStatic
            ):  # I don't know how to get the static modifier from the property with reflection
                property.static = True
            if get_method.IsPublic and get_method.IsStatic:
                property.value = prop.GetValue(None, None)
        set_method = prop.SetMethod
        if set_method:
            if class_type.IsInterface or set_method.IsPublic:
                property.setter = True

        # ----- to test the setter only properties, there wasn't another example handy so I hacked this..
        #       also had to hack to add published to the interface in C# (filed bug about this)
        # if prop.Name == "ObjectId" and class_type.Name == "IDataModelObject":
        #    property.getter=False
        #    property.setter=True
        # -----

        output.append(property)
    return output


def write_property(
    buffer: typing.TextIO, prop: Property, indent_level: int = 1
) -> None:
    logging.debug(f"        writing property {prop.name}")
    indent = "    " * indent_level
    if prop.static:
        # this only works for autocomplete for python 3.9+
        assert (
            prop.getter and not prop.setter
        ), "Don't deal with public static getter+setter"
        buffer.write(f"{indent}@classmethod\n")
        buffer.write(f"{indent}@property\n")
        buffer.write(f"{indent}def {prop.name}(cls) -> typing.Optional[{prop.type}]:\n")
        indent = "    " * (1 + indent_level)

        write_docstring(buffer, prop.doc, indent_level + 1)

        if prop.value:
            if (type(prop.value) is not type(1)) and ("`" in f"{prop.value}"):
                prop.value = fix_str(f"{prop.value}")

            buffer.write(f"{indent}return {prop.value}\n")
        else:
            buffer.write(f"{indent}return None\n")
    else:
        if prop.setter and not prop.getter:
            # setter only, can't use @property, use python builtin-property feature
            buffer.write(
                f"{indent}def {prop.name}(self, newvalue: typing.Optional[{prop.type}]) -> None:\n"
            )
            indent = "    " * (1 + indent_level)
            write_docstring(buffer, prop.doc, indent_level + 1)
            buffer.write(f"{indent}return None\n")
            buffer.write("\n")
            indent = "    " * (indent_level)
            buffer.write(f"{indent}{prop.name} = property(None, {prop.name})\n")
        else:
            assert prop.getter
            buffer.write(f"{indent}@property\n")
            buffer.write(
                f"{indent}def {prop.name}(self) -> typing.Optional[{prop.type}]:\n"
            )
            indent = "    " * (1 + indent_level)
            write_docstring(buffer, prop.doc, indent_level + 1)
            buffer.write(f"{indent}return None\n")
    buffer.write("\n")


def write_method(buffer: typing.TextIO, method: Method, indent_level: int = 1) -> None:
    logging.debug(f"        writing method {method.name}")
    indent = "    " * indent_level
    if method.static:
        buffer.write(f"{indent}@classmethod\n")
        first_arg = "cls"
    else:
        first_arg = "self"
    args = [first_arg] + [f'{arg.name}: "{arg.type}"' for arg in method.args]
    args = f"({', '.join(args)})"
    buffer.write(f"{indent}def {method.name}{args} -> {method.return_type}:\n")
    indent = "    " * (1 + indent_level)
    write_docstring(buffer, method.doc, indent_level + 1)
    buffer.write(f"{indent}pass\n")
    buffer.write("\n")


def get_methods(
    class_type: typing.Any,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> typing.List[Method]:
    # TODO - base class properties are not handled here. They might be published if they are ansys types
    #        or not if they are system types (e.g. the IList methods implemented by an Ansys type that derives from System.Collections.Generic.IList)
    methods = [
        prop
        for prop in class_type.GetMethods()
        if (type_filter is None or type_filter(prop))
    ]
    output = []
    for method in methods:
        method_return_type = f'"{fix_str(method.ReturnType.ToString())}"'
        method_name = method.Name
        params = method.GetParameters()
        args = [
            Param(type=fix_str(param.ParameterType.ToString()), name=param.Name)
            for param in params
        ]
        full_method_name = method_name + f"({','.join([fix_str(arg.type) for arg in args])})"
        declaring_type_name = method.DeclaringType.ToString()
        method_doc_key = f"M:{declaring_type_name}.{full_method_name}"
        method_doc = doc.get(method_doc_key, None)
        method = Method(
            name=method_name,
            doc=method_doc,
            return_type=method_return_type,
            static=method.IsStatic,
            args=args,
        )
        output.append(method)
    return output


def write_class(
    buffer: typing.TextIO,
    class_type: typing.Any,
    namespace: str,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> None:
    logging.debug(f"    writing class {class_type.Name}")
    buffer.write(f"class {class_type.Name}(object):\n")
    class_doc = doc.get(f"T:{namespace}.{class_type.Name}", None)
    write_docstring(buffer, class_doc, 1)
    buffer.write("\n")
    props = get_properties(class_type, doc, type_filter)
    [write_property(buffer, prop, 1) for prop in props]
    methods = get_methods(class_type, doc, type_filter)
    [write_method(buffer, method, 1) for method in methods]

    # TODO - constructor

    if len(props) == 0 and len(methods) == 0:
        buffer.write("    pass\n")
    buffer.write("\n")


def write_module(
    namespace: str,
    mod_types: typing.List,
    doc: typing.Dict[str, DocMember],
    outdir: str,
    type_filter: typing.Callable = None,
) -> None:
    outdir = pathlib.Path(outdir)
    for token in namespace.split("."):
        outdir = outdir / token
    logging.info(f"Writing to {str(outdir.resolve())}")
    outdir.mkdir(exist_ok=True, parents=True)
    class_types = [
        mod_type for mod_type in mod_types if mod_type.IsClass or mod_type.IsInterface
    ]
    enum_types = [mod_type for mod_type in mod_types if mod_type.IsEnum]
    logging.info(f"Writing to {str(outdir.resolve())}")
    with open(outdir / "__init__.py", "w", encoding="utf-8") as f:
        # TODO - jinja
        if len(enum_types) > 0:
            f.write("from enum import Enum\n")
        f.write("import typing\n\n")
        logging.info(f"    {len(enum_types)} enum types")
        for enum_type in enum_types:
            write_enum(f, enum_type, namespace, doc, type_filter)
        for class_type in class_types:
            write_class(f, class_type, namespace, doc, type_filter)
    logging.info(f"Done processing {namespace}")


def load_doc(xml_path: str) -> ET:
    """Get a dictionary of doc entities from the Assembly documentation file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    members = root.find("members")
    doc_members = [DocMember(member) for member in members]
    output = {doc_member.name: doc_member for doc_member in doc_members}
    return output


def get_doc(assembly: "System.Reflection.RuntimeAssembly"):
    """Get the documentation file from assembly, or None if it doesn't exist."""
    uri = System.UriBuilder(assembly.CodeBase)
    path = System.Uri.UnescapeDataString(uri.Path)
    directory = System.IO.Path.GetDirectoryName(path)
    xml_path = System.IO.Path.Combine(directory, assembly.GetName().Name + ".xml")
    if System.IO.File.Exists(xml_path):
        logging.info(f"Loading xml doc from {xml_path}")
        doc = load_doc(xml_path)
        return doc
    else:
        logging.warning("XML Doc file does not exist, skipping")
        return None


def get_namespaces(
    assembly: "System.Reflection.RuntimeAssembly", type_filter: typing.Callable = None
) -> typing.Dict:
    """Get all the namespaces and filtered types in the assembly given by assembly_name."""
    logging.info(
        f"    Getting types from the {os.path.basename(assembly.CodeBase)} assembly"
    )
    namespaces = crawl_loaded_references(assembly, type_filter)
    return namespaces


def make(outdir: str, assembly_name: str, type_filter: typing.Callable = None) -> None:
    """Generate python stubs for an assembly."""
    logging.info(f"Loading assembly {assembly_name}")
    assembly = clr.AddReference(assembly_name)
    if type_filter is not None:
        logging.info(f"   Using a type_filter: {str(type_filter)}")
    namespaces = get_namespaces(assembly, type_filter)
    dump_types(namespaces)
    doc = get_doc(assembly)
    logging.info(f"    {len(namespaces.items())} namespaces")
    for namespace, mod_types in namespaces.items():
        logging.info(f"Processing {namespace}")
        logging.info(f"   {len(namespaces.items())} namespaces")
        write_module(namespace, mod_types, doc, outdir, type_filter)
        logging.info(f"Done processing {namespace}")
