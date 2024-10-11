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

"""Module containing routine to generate python stubs for an assembly."""

from dataclasses import dataclass
import json
import logging
import pathlib
import re
import typing
import xml.etree.ElementTree as ElementTree

import clr
import System

C_TO_PYTHON = {
    "System.Boolean": "bool",
    "System.Collections.Generic.IDictionary": "dict",
    "System.Collections.Generic.IEnumerable": "typing.Iterable",
    "System.Collections.Generic.IEnumerator": "typing.Iterator",
    "System.Collections.Generic.IList": "list",
    "System.Collections.Generic.IReadOnlyDictionary": "dict",
    "System.Collections.Generic.IReadOnlyList": "tuple",
    "System.Collections.Generic.KeyValuePair": "dict",
    "System.Collections.Generic.List": "list",
    "System.Collections.ICollection": "typing.Collection",
    "System.Collections.IEnumerable": "typing.Iterable",
    "System.Collections.IEnumerator": "typing.Iterator",
    "System.DateTime": "typing.Any",
    "System.Double": "float",
    # "System.IAsyncResult": "",
    # "System.IDisposable": "",
    # "System.Func": "",
    "System.Int32": "int",
    "System.Object": "typing.Any",
    "System.String": "str",
    "System.Tuple": "tuple",
    "System.Type": "type",
    "System.UInt32": "int",
    "System.Void": "None",
}


def c_types_to_python(type_str):
    """Replace C# types with Python types.

    Parameters
    ----------
    type_str: str
        String containing C# type.
    """
    for key, value in C_TO_PYTHON.items():
        # Replace C# type with Python type
        type_str = type_str.replace(key, value)

        if '"' in type_str:
            # Remove double quotes from type
            type_str = type_str.replace('"', "")

    # Wrap strings that contain Ansys or ChildrenType in quotes
    ansys_regex = re.compile("(Ansys[^],]*|ChildrenType)")
    matches = ansys_regex.findall(type_str)
    for match in matches:
        type_str = re.sub(ansys_regex, f'"{match}"', type_str)

    return type_str


def is_namespace(something):
    """Check if an object is a namespace.

    Parameters
    ----------
    something: object
        Object to check if it's a namespace

    Returns
    -------
    bool
        True if object is Namespace: Module
        False if object is not Namespace: Module
    """
    if isinstance(something, type(System)):
        return True


def iter_module(module, type_filter: typing.Callable = None):
    """Recursively iterates through all namespaces in assembly.

    Parameters
    ----------
    module: System.Reflection.RuntimeAssembly
        An assembly module
    type_filter: typing.Callable
        Whether or not the type is published

    Returns
    -------
    string
        The namespace in the assembly file
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


def crawl_loaded_references(
    assembly: "System.Reflection.RuntimeAssembly", type_filter: typing.Callable = None
) -> dict:
    """Crawl Loaded assemblies to get Namespaces.

    Parameters
    ----------
    assembly: System.Reflection.RuntimeAssembly
        An assembly. For example, Ansys.ACT.WB1.
    type_filter: typing.Callable
        Whether or not the type is published

    Returns
    -------
    dict
        Dictionary of namespaces in the assembly
    """
    return iter_module(assembly, type_filter)


def dump_types(namespaces: dict):
    """Crawl Loaded assemblies to get Namespaces.

    Parameters
    ----------
    namespaces: dict
        Dictionary of namespaces in the assembly
    """
    printable_namespaces = {k: [x.Name for x in v] for k, v in namespaces.items()}
    logging.debug(json.dumps(printable_namespaces, indent=2, sort_keys=True))


class DocMember:
    """Docstring member."""

    def __init__(self, element: ElementTree.Element):
        self._element = element

    @classmethod
    def __get_element_text(cls, element: typing.Optional[ElementTree.Element]):
        """Get the text of an element."""
        if element is None:
            return None
        return element.text

    @property
    def name(self) -> str:
        """The name within the element."""
        return self._element.attrib["name"]

    @property
    def summary(self) -> str:
        """The summary within the element."""
        summary = self._element.find("summary")
        summary_text = None

        if summary is not None:
            summary_text = summary.text
            # Get text from tags in the summary text if necessary
            for tags in summary:
                if "paramref" in tags.tag:
                    # Get the text of the member's (self._element's) parameter
                    param_text = self._element.find("param").text
                    # Remove period from end of parameter text
                    if param_text[-1] == ".":
                        param_text = param_text[:-1]
                    # Make first letter of parameter text lowercase
                    if param_text[0].isupper():
                        param_text = param_text[0].lower() + param_text[1:]
                    # Append the parameter text to the summary_text string
                    summary_text += param_text
                    # Append the text after the param tag to the summary_text
                    summary_text += tags.tail
                else:
                    for key in tags.attrib:
                        # Append the text of the key of a tag to the summary_text
                        summary_text += tags.attrib.get(key)
                        if tags.tail is not None:
                            # Append the text after the tag to the summary_text if it exists
                            summary_text += tags.tail

        return summary_text

    @property
    def params(self) -> str:
        """The parameters within a element."""
        return self._element.findall("param")

    @property
    def remarks(self) -> str:
        """The remarks within the element."""
        return self.__get_element_text(self._element.find("remarks"))

    @property
    def example(self) -> ElementTree.Element:
        """The example within the element."""
        return self._element.find("example")


def write_docstring(
    buffer: typing.TextIO, doc_member: typing.Optional[DocMember], indent_level=1
) -> None:
    """Write docstring of class or enum with the given indentation level, if available.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the docstring
    doc_member: typing.Optional[DocMember]
        A member's name, summary, params, remarks, and examples
    indent_level: int
        ``1`` to write one indent
    """
    if doc_member is None:
        return
    summary = doc_member.summary
    # print(summary)
    if summary is None:
        return
    indent = "    " * indent_level
    buffer.write(f'{indent}"""\n')
    buffer.write(f"{indent}{summary}\n")
    buffer.write(f'{indent}"""\n')


ENUM_VALUE_REPLACEMENTS = {"None": "None_", "True": "True_"}


def write_enum_field(buffer: typing.TextIO, field: typing.Any, indent_level: int = 1) -> None:
    """Write an enum field.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the docstring
    field: typing.Any
        The field information from System.Reflection.MdFieldInfo
    indent_level: int
        ``1`` to write one indent
    """
    name = field.Name
    # logging.debug(f"        writing enum value {name}")
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
    """Write an enum.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the docstring
    enum_type: typing.Any
        The enum type
    namespace: str
        The namespace of the enum
    doc: typing.Dict[str, DocMember]
        A DocMember or string that holds information about the enum.
    type_filter: typing.Callable = None
        Whether or not the type is published.
    """
    # logging.debug(f"    writing enum {enum_type.Name}")
    fields = [
        field
        for field in enum_type.GetFields()
        if field.IsLiteral and (type_filter is None or type_filter(field))
    ]
    buffer.write(f"class {enum_type.Name}(Enum):\n")
    enum_doc = doc.get(f"T:{namespace}.{enum_type.Name}", None)
    if enum_doc is None:
        write_missing_class_enum_docstring(buffer, enum_type.Name, "enum")
    else:
        write_docstring(buffer, enum_doc, 1)
    buffer.write("\n")
    for field in fields:
        write_enum_field(buffer, field, 1)
    if len(fields) == 0:
        buffer.write("    pass\n")
    buffer.write("\n")


# Helper for fix_str()
def remove_backtick(input_str: str):
    """Remove backticks from a given string.

    Parameters
    ----------
    input_str: str
        A string that could contain backticks

    Returns
    -------
    str
        A string without backticks
    """
    backtick = input_str.index("`")
    new_str = input_str[0:backtick] + input_str[backtick + 2 :]

    if "`" in new_str:
        return remove_backtick(new_str)
    else:
        return new_str


# Helper for get_properties() and write_properties
def fix_str(input_str: str):
    """Replace incorrect special characters in strings.

    Parameters
    ----------
    input_str: str
        A string that could contain backticks

    Returns
    -------
    str
        A string that doesn't have special characters
    """
    if "+" in input_str:
        input_str = input_str.replace("+", ".")
    if "[]" in input_str:
        input_str = input_str.replace("[]", "")
    if "`" in input_str:
        input_str = remove_backtick(input_str)
    return input_str


@dataclass
class Param:
    """Param class."""

    type: str
    name: str


@dataclass
class Method:
    """Method class."""

    name: str
    doc: DocMember
    return_type: str
    static: bool
    args: typing.List[Param]


@dataclass
class Property:
    """Property class."""

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
    """Get information from properties and store it in the Property object.

    Parameters
    ----------
    class_type: typing.Any
        The class type.
    doc: typing.Dict[str, DocMember]
        A DocMember or string that holds information about the property.
    type_filter: typing.Callable = None
        Whether or not the type is published.

    Returns
    -------
    typing.List[Property]
        A list of properties
    """
    props = [
        prop for prop in class_type.GetProperties() if (type_filter is None or type_filter(prop))
    ]
    output = []
    for prop in props:
        prop_type = f'"{prop.PropertyType.ToString()}"'
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


def write_property(buffer: typing.TextIO, prop: Property, indent_level: int = 1) -> None:
    """Write a property.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the docstring
    prop: Property
        A Property object containing information about the property
    indent_level: int
        ``1`` to write one indent
    """
    # logging.debug(f"        writing property {prop.name}")
    indent = "    " * indent_level

    prop_type = fix_str(prop.type)
    prop_type = c_types_to_python(prop_type)

    if prop.static:
        # this only works for autocomplete for python 3.9+
        assert prop.getter and not prop.setter, "Don't deal with public static getter+setter"
        buffer.write(f"{indent}@classmethod\n")
        buffer.write(f"{indent}@property\n")
        buffer.write(f"{indent}def {prop.name}(cls) -> typing.Optional[{prop_type}]:\n")
        indent = "    " * (1 + indent_level)
        if prop.doc is None:
            write_missing_prop_method_docstring(buffer, prop, "property", indent_level + 1)
        else:
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
                f"{indent}def {prop.name}(self, newvalue: typing.Optional[{prop_type}]) -> None:\n"
            )
            indent = "    " * (1 + indent_level)
            if prop.doc is None:
                write_missing_prop_method_docstring(buffer, prop, "property", indent_level + 1)
            else:
                write_docstring(buffer, prop.doc, indent_level + 1)
            buffer.write(f"{indent}return None\n")
            buffer.write("\n")
            indent = "    " * (indent_level)
            buffer.write(f"{indent}{prop.name} = property(None, {prop.name})\n")
        else:
            assert prop.getter
            buffer.write(f"{indent}@property\n")
            buffer.write(f"{indent}def {prop.name}(self) -> typing.Optional[{prop_type}]:\n")
            indent = "    " * (1 + indent_level)
            if prop.doc is None:
                write_missing_prop_method_docstring(buffer, prop, "property", indent_level + 1)
            else:
                write_docstring(buffer, prop.doc, indent_level + 1)
            buffer.write(f"{indent}return None\n")
    buffer.write("\n")


def write_missing_class_enum_docstring(buffer, name, obj_type):
    """Write a docstring for classes and enums that do not contain a docstring in the XML file.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the docstring
    name: str
        The name of an interface
    obj_type: str
        The object type of the interface
    """
    indent = "    " * 1
    buffer.write(f'{indent}"""\n')
    if obj_type == "class":
        if name[0] == "I":
            buffer.write(f"{indent}{name} interface.\n")
        else:
            buffer.write(f"{indent}{name} {obj_type}.\n")
    buffer.write(f'{indent}"""\n')


def write_missing_prop_method_docstring(buffer, obj, obj_type, indent_level):
    """Write a docstring for methods and properties that do not contain a docstring in the XML file.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the docstring
    obj: generate_content.Method or generate_content.Property
        A method or property object
    obj_type: type
        The object type of the interface
    indent_level: int
        ``1`` to indent a line once
    """
    indent = "    " * indent_level
    buffer.write(f'{indent}"""\n')
    if obj.name == "GetChildren":
        buffer.write(f"{indent}Gets the list of children, filtered by type.\n")
    else:
        buffer.write(f"{indent}{obj.name} {obj_type}.\n")
    buffer.write(f'{indent}"""\n')


def write_method(buffer: typing.TextIO, method: Method, indent_level: int = 1) -> None:
    """Write a method.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the method
    method: Method
        A Method object
    indent_level: int
        ``1`` to indent a line once
    """
    indent = "    " * indent_level
    if method.static:
        buffer.write(f"{indent}@classmethod\n")
        first_arg = "cls"
    else:
        first_arg = "self"
    args = [first_arg] + [f"{arg.name}: {c_types_to_python(arg.type)}" for arg in method.args]
    args = f"({', '.join(args)})"
    method_type = c_types_to_python(method.return_type)

    buffer.write(f"{indent}def {method.name}{args} -> {method_type}:\n")
    indent = "    " * (1 + indent_level)
    if method.doc is None:
        write_missing_prop_method_docstring(buffer, method, "method", indent_level + 1)
    else:
        write_docstring(buffer, method.doc, indent_level + 1)
    buffer.write(f"{indent}pass\n")
    buffer.write("\n")


def adjust_method_name_xml(method_name: str):
    """Adjust the method name to find docstring in XML.

    Parameters
    ----------
    method_name: str
        The method name
    """
    # GetChildren(System...) is GetChildren``1(System...) in the XML file
    if ".GetChildren(System" in method_name:
        method_name = method_name.replace(".GetChildren(System", ".GetChildren``1(System")
    # IList`1[ChildrenType] is IList{``0} in the XML file
    if "IList`1[ChildrenType]" in method_name:
        method_name = method_name.replace("IList`1[ChildrenType]", "IList{``0}")
    # IList`1[Ansys...] is IList{Ansys...} in the XML file
    # IEnumerable`1[Ansys...]` is IEnumerable{Ansys...} in the XML file
    if "`1[Ansys" in method_name:
        method_name = method_name.replace("`1[Ansys", "{Ansys").replace("]", "}")
    if "`2[Ansys" in method_name:
        method_name = method_name.replace("`2[Ansys", "{Ansys").replace("]", "}")
    # IEnumerable`1[System.Object] is IEnumerable{System.Object} in the XML file
    if "IEnumerable`1[System" in method_name:
        method_name = method_name.replace("IEnumerable`1[System", "IEnumerable{System").replace(
            "]", "}"
        )
    if "+" in method_name:
        method_name = method_name.replace("+", ".")

    return method_name


def get_methods(
    class_type: typing.Any,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> typing.List[Method]:
    """Get information from methods and store it in the Method object.

    Parameters
    ----------
    class_type: typing.Any
        The class type.
    doc: typing.Dict[str, DocMember]
        A DocMember or string that holds information about the method.
    type_filter: typing.Callable = None
        Whether or not the type is published.

    Returns
    -------
    typing.List[Method]
        A list of methods
    """
    methods = [
        prop for prop in class_type.GetMethods() if (type_filter is None or type_filter(prop))
    ]
    output = []
    for method in methods:
        method_return_type = f'"{method.ReturnType.ToString()}"'
        method_name = method.Name
        params = method.GetParameters()
        args = [
            Param(type=fix_str(param.ParameterType.ToString()), name=param.Name) for param in params
        ]
        full_method_name = method_name + f"({','.join([arg.type for arg in args])})"
        declaring_type_name = method.DeclaringType.ToString()

        # Get the method name
        method_doc_key = f"M:{declaring_type_name}.{full_method_name}".replace("()", "")
        method_doc_key = adjust_method_name_xml(method_doc_key)
        method_doc = doc.get(method_doc_key, None)

        method = Method(
            name=method_name,
            doc=method_doc,
            return_type=fix_str(method_return_type),
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
    """Write a class.

    Parameters
    ----------
    buffer: typing.TextIO
        The buffer for writing the class
    class_type: typing.Any
        The class type object
    namespace: str
        The namespace of the class being written
    doc: typing.Dict[str, DocMember]
        A DocMember or string that holds information about the class.
    type_filter: typing.Callable = None
        Whether or not the type is published
    """
    # logging.debug(f"    writing class {class_type.Name}")
    buffer.write(f"class {class_type.Name}(object):\n")
    class_doc = doc.get(f"T:{namespace}.{class_type.Name}", None)
    if class_doc is None:
        write_missing_class_enum_docstring(buffer, class_type.Name, "class")
    else:
        write_docstring(buffer, class_doc, 1)
    buffer.write("\n")
    props = get_properties(class_type, doc, type_filter)
    [write_property(buffer, prop, 1) for prop in props]
    methods = get_methods(class_type, doc, type_filter)
    [write_method(buffer, method, 1) for method in methods]

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
    """Write a module.

    Parameters
    ----------
    mod_type: typing.Any
        The module type object
    doc: typing.Dict[str, DocMember]
        A DocMember or string that holds information about the class.
    outdir: str
        The path of the file that contains the module.
    type_filter: typing.Callable = None
        Whether or not the type is published
    """
    outdir = pathlib.Path(outdir)
    for token in namespace.split("."):
        outdir = outdir / token
    # logging.info(f"Writing to {str(outdir.resolve())}")
    outdir.mkdir(exist_ok=True, parents=True)
    class_types = [mod_type for mod_type in mod_types if mod_type.IsClass or mod_type.IsInterface]
    enum_types = [mod_type for mod_type in mod_types if mod_type.IsEnum]
    # logging.info(f"Writing to {str(outdir.resolve())}")
    with pathlib.Path.open(outdir / "__init__.py", "w", encoding="utf-8") as f:
        f.write(f'"""{pathlib.PurePath(outdir).name} subpackage."""\n')
        if len(enum_types) > 0:
            f.write("from enum import Enum\n")
        f.write("import typing\n\n")
        # logging.info(f"    {len(enum_types)} enum types")
        for enum_type in enum_types:
            write_enum(f, enum_type, namespace, doc, type_filter)
        for class_type in class_types:
            write_class(f, class_type, namespace, doc, type_filter)
    # logging.info(f"Done processing {namespace}")


def load_doc(xml_path: str) -> ElementTree:
    """Get a dictionary of doc entities from the Assembly documentation file.

    Parameters
    ----------
    xml_path: str
        The path to the XML file

    Returns
    -------
    ElementTree
        An element tree of the information from the assembly XML file
    """
    tree = ElementTree.parse(xml_path)
    root = tree.getroot()
    members = root.find("members")
    doc_members = [DocMember(member) for member in members]
    # 'M:Ansys.ACT.Automation.Mechanical.VirtualCell.GetChildren``1(System.Boolean,System.Collections.Generic.IList{``0})': <gen.DocMember object at 0x0000018B1F50A050>
    output = {doc_member.name: doc_member for doc_member in doc_members}
    return output


def get_doc(assembly: "System.Reflection.RuntimeAssembly"):
    """Get the documentation file from assembly, or None if it doesn't exist.

    Parameters
    ----------
    assembly: "System.Reflection.RuntimeAssembly"
        An assembly. For example, Ansys.ACT.WB1.
    """
    uri = System.UriBuilder(assembly.CodeBase)
    path = System.Uri.UnescapeDataString(uri.Path)
    directory = System.IO.Path.GetDirectoryName(path)
    xml_path = System.IO.Path.Combine(directory, assembly.GetName().Name + ".xml")
    if System.IO.File.Exists(xml_path):
        # logging.info(f"Loading xml doc from {xml_path}")
        doc = load_doc(xml_path)
        return doc
    else:
        # logging.warning("XML Doc file does not exist, skipping")
        return None


def get_namespaces(
    assembly: "System.Reflection.RuntimeAssembly", type_filter: typing.Callable = None
) -> typing.Dict:
    """Get all the namespaces and filtered types in the assembly given by assembly_name.

    Parameters
    ----------
    assembly: "System.Reflection.RuntimeAssembly"
        An assembly
    type_filter:
        Whether or not the type is published

    Returns
    -------
    typing.Dict
        A dictionary of published namespaces within the assembly
    """
    # logging.info(f"    Getting types from the {pathlib.PurePath(assembly.CodeBase).name} assembly")
    namespaces = crawl_loaded_references(assembly, type_filter)
    return namespaces


def make(outdir: str, assembly_name: str, type_filter: typing.Callable = None) -> None:
    """Generate Python stubs for an assembly.

    Parameters
    ----------
    outdir: str
        The directory where modules are being written to.
    assembly_name: str
        The name of the assembly
    type_filter: typing.Callable
        Whether or not a type is published
    """
    # logging.info(f"Loading assembly {assembly_name}")
    assembly = clr.AddReference(assembly_name)
    # if type_filter is not None:
    # logging.info(f"   Using a type_filter: {str(type_filter)}")
    # Type filter is what gets messed up
    namespaces = get_namespaces(assembly, type_filter)
    dump_types(namespaces)
    doc = get_doc(assembly)
    # logging.info(f"    {len(namespaces.items())} namespaces")
    for namespace, mod_types in namespaces.items():
        if "DesignModeler" not in namespace:
            # logging.info(f"Processing {namespace}")
            # logging.info(f"   {len(namespaces.items())} namespaces")
            write_module(namespace, mod_types, doc, outdir, type_filter)
            # logging.info(f"Done processing {namespace}")
