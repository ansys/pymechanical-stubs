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

ENUM_VALUE_REPLACEMENTS = {"None": "None_", "True": "True_"}


#### Get Namespaces ####
def get_namespaces(
    assembly: "System.Reflection.RuntimeAssembly", type_filter: typing.Callable = None
) -> typing.Dict:
    """Get all the namespaces and filtered types in the assembly given by assembly_name."""
    # logging.info(
    #     f"    Getting types from the {os.path.basename(assembly.CodeBase)} assembly"
    # )
    namespaces = crawl_loaded_references(assembly, type_filter)
    return namespaces


# Helper for get_namespaces()
def crawl_loaded_references(assembly, type_filter: typing.Callable = None) -> dict:
    """Crawl Loaded assemblies to get Namespaces."""
    return iter_module(assembly, type_filter)


# Helper for crawl_loaded_references()
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


#### Dump types ####
def dump_types(namespaces):
    printable_namespaces = {k: [x.Name for x in v] for k, v in namespaces.items()}
    # logging.debug(json.dumps(printable_namespaces, indent=2, sort_keys=True))


#### Get doc ####
def get_doc(assembly: "System.Reflection.RuntimeAssembly"):
    """Get the documentation file from assembly, or None if it doesn't exist."""
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


def load_doc(xml_path: str) -> ET:
    """Get a dictionary of doc entities from the Assembly documentation file."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    members = root.find("members")
    doc_members = [DocMember(member) for member in members]
    output = {doc_member.name: doc_member for doc_member in doc_members}
    return output


#################################################################################
# This is where it starts writing the init files from the xml files
# Above this, it's searching for the xml files provided


#### Write Module ####
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


# Write Module
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
    # logging.info(f"Writing to {str(outdir.resolve())}")
    outdir.mkdir(exist_ok=True, parents=True)
    class_types = [
        mod_type for mod_type in mod_types if mod_type.IsClass or mod_type.IsInterface
    ]
    enum_types = [mod_type for mod_type in mod_types if mod_type.IsEnum]
    # logging.info(f"Writing to {str(outdir.resolve())}")
    with open(outdir / "__init__.py", "w", encoding="utf-8") as f:
        # TODO - jinja
        if len(enum_types) > 0:
            f.write("from enum import Enum\n")
        f.write("import typing\n\n")
        # logging.info(f"    {len(enum_types)} enum types")
        for enum_type in enum_types:
            write_enum(f, enum_type, namespace, doc, type_filter)
        for class_type in class_types:
            write_class(f, class_type, namespace, doc, type_filter)
    # logging.info(f"Done processing {namespace}")


#### Write Enum ####
# Helper for write_module()
def write_enum(
    buffer: typing.TextIO,
    enum_type: typing.Any,
    namespace: str,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> None:
    # logging.debug(f"    writing enum {enum_type.Name}")
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


# Helper for write_enum() and write_class()
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


# Helper for write_enum()
def write_enum_field(
    buffer: typing.TextIO, field: typing.Any, indent_level: int = 1
) -> None:
    name = field.Name
    # logging.debug(f"        writing enum value {name}")
    int_value = field.GetRawConstantValue()
    str_value = ENUM_VALUE_REPLACEMENTS.get(name, name)
    indent = "    " * indent_level
    buffer.write(f"{indent}{str_value} = {int_value}\n")


#### Write Class ####
# Helper for write_module()
def write_class(
    buffer: typing.TextIO,
    class_type: typing.Any,
    namespace: str,
    doc: typing.Dict[str, DocMember],
    type_filter: typing.Callable = None,
) -> None:
    # logging.debug(f"    writing class {class_type.Name}")
    # Write the class
    buffer.write(f"class {class_type.Name}(object):\n")
    class_doc = doc.get(f"T:{namespace}.{class_type.Name}", None)
    # Write the docstring for the class
    write_docstring(buffer, class_doc, 1)
    buffer.write("\n")

    # Generate a list of each of the properties
    props = get_properties(class_type, doc, type_filter)
    methods = [
        prop
        for prop in class_type.GetMethods()
        if (type_filter is None or type_filter(prop))
    ]

    # Write import statements properties and methods
    import_statements = get_imports(props, methods, 1)
    for statement in import_statements:
        buffer.write(f"{statement}\n")
    buffer.write("\n")

    # Generate a list of methods
    methods = get_methods(class_type, doc, type_filter)

    # Write each property within the class
    [write_property(buffer, prop, 1) for prop in props]
    # Write each method inside the class
    [write_method(buffer, method, 1) for method in methods]

    # TODO - constructor

    if len(props) == 0 and len(methods) == 0:
        buffer.write("    pass\n")
    buffer.write("\n")


@dataclass
class Property:
    name: str
    type: str
    getter: bool
    setter: bool
    doc: DocMember
    static: bool
    value: typing.Optional[typing.Any]  # may be used if static


# Helper for write_class()
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

        # property examples:
        # Property(name='VisibleProperties', type='"System.Collections.Generic.IReadOnlyList[Ansys.ACT.Automation.Mechanical.Property]"',
        # getter=True, setter=False, doc=<gen.DocMember object at 0x000001CA7904DDE0>, static=False, value=None)
        #
        # Property(name='MultiplierEntry', type='"Ansys.Mechanical.DataModel.Enums.AMMultiplierEntryType"',
        # getter=True, setter=True, doc=<gen.DocMember object at 0x000001CA5D4D1300>, static=False, value=None)
        output.append(property)
    return output


def dict_import_helper(check_str, import_dict):
    """Add import to import_dict"""
    if "Ansys" in check_str:
        # Remove double quotes
        check_str = check_str.replace('"', '')

        # Only get the phrase containing Ansys
        # Ex: Ansys.ACT.Automation.Mechanical.CrossSections
        if "]" in check_str:
            ansys_index = check_str.index("Ansys")
            check_str = check_str[ansys_index:].replace("]", "")

            if "," in check_str:
                str_list = check_str.split(",")
                for string in str_list:
                    if "Ansys" in string:
                        import_dict = manipulate_str(string, import_dict)
        else:
            import_dict = manipulate_str(check_str, import_dict)

    return import_dict


def manipulate_str(check_str, import_dict):
    beginning_str = ".".join(check_str.split(".")[1:-1])
    if beginning_str not in import_dict:
        import_dict[beginning_str] = set()
    end_str = check_str.split(".")[-1]

    if "+" in end_str:
        sep_str = end_str.split("+")
        for item in sep_str:
            import_dict[beginning_str].add(item)
    elif "]" in end_str:
        end_str = end_str.replace("]", "")
    else:
        import_dict[beginning_str].add(end_str)

    return import_dict



def get_imports(props, methods, indent_level: int = 1) -> None:
    """Create import statements for properties and methods."""
    import_list = []
    import_dict = {}
    indent = "    " * indent_level

    # Get import statements for property types
    for prop in props:
        import_dict = dict_import_helper(prop.type, import_dict)

    # Get import statements for method return types and parameter types
    for method in methods:
        return_type = fix_str(method.ReturnType.ToString())
        import_dict = dict_import_helper(return_type, import_dict)

        params = fix_str(method.GetParameters())
        for param in params:
            import_dict = dict_import_helper(param.ParameterType.ToString(), import_dict)

    # Append all import statements to list
    for key, value in import_dict.items():
        value_list = list(value)
        value_str = ", ".join(value_list).replace('"', '')
        key = key.replace('"', '')

        import_list.append(f"{indent}from ansys.mechanical.stubs.Ansys.{key} import {value_str}")

    return list(set(import_list))


def python_type(prop_name, prop_type):
    type_dict = {"System.Boolean": "bool", "System.String": "str", "System.Double": "float", "System.Int32": "int",
                 "System.Int": "int", "System.Void": "None", "System.Collections.Generic.IEnumerable": "enumerate",
                 "System.Object": "object", "System.Collections.Generic.KeyValuePair": "dict",
                 "System.Collections.Generic.IDictionary": "dict", "System.Collections.Generic.IReadOnlyList": "tuple",
                 "System.Collections.Generic.IList": "list", "System.UInt32": "int"}

    # Should System.UInt32 be int, or int + 2**32?
    for key,value in type_dict.items():
        if key in prop_type:
            prop_type = prop_type.replace(key, value)

    prop_type = prop_type.replace('"', '')
    if "Ansys" in prop_type:
        ans_index = prop_type.index("Ansys")
        if ans_index == 0:
            module = prop_type.split('.')
            joined_module = ".".join(module[1:])
            class_name = module[-1]
            if prop_name == class_name:
                return f'"{joined_module}"'
            else:
                return f'"{class_name}"'
        else:
            bracket_index = prop_type.index("]")
            module = prop_type[ans_index:bracket_index].split('.')
            joined_module = ".".join(module[1:])
            class_name = module[-1]

            if prop_name == class_name:
                return prop_type.replace(".".join(module), f'"{joined_module}"')
            else:
                return prop_type.replace(".".join(module), f'"{class_name}"')
    else:
        return prop_type

    # @property
    # def Environments(self) -> typing.Iterable["Analysis"]:


# Helper for write_class()
def write_property(
    buffer: typing.TextIO, prop: Property, indent_level: int = 1
) -> None:
    # logging.debug(f"        writing property {prop.name}")
    indent = "    " * indent_level
    if prop.static:
        # @property
        # def InternalObject(self) -> typing.Optional["Ansys.Common.Interop.DSObjectsAuto.IDSGeometryImportGroupAuto"]:
        #     """
        #     Gets the internal object. For advanced usage only.
        #     """
        #     return None

        # this only works for autocomplete for python 3.9+
        assert (
            prop.getter and not prop.setter
        ), "Don't deal with public static getter+setter"
        buffer.write(f"{indent}@classmethod\n")
        buffer.write(f"{indent}@property\n")

        buffer.write(f"{indent}def {prop.name}(cls) -> {python_type(prop.name, prop.type)}:\n")
        indent = "    " * (1 + indent_level)

        write_docstring(buffer, prop.doc, indent_level + 1)

        if prop.value:
            if (type(prop.value) is not type(1)) and ("`" in f"{prop.value}"):
                prop.value = fix_str(f"{prop.value}")

            buffer.write(f"{indent}return {prop.value}\n")
        else:
            buffer.write(f"{indent}return None\n")
    else:
        # def SetLocation(self, newvalue: typing.Optional["Ansys.ACT.Interfaces.Common.ISelectionInfo"]) -> None:
        #     """
        #     Sets the point location.
        #     """
        #     return None
        #
        # SetLocation = property(None, SetLocation)

        if prop.setter and not prop.getter:
            # setter only, can't use @property, use python builtin-property feature
            buffer.write(
                f"{indent}def {prop.name}(self, newvalue: {python_type(prop.name, prop.type)}) -> None:\n"
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
                f"{indent}def {prop.name}(self) -> {python_type(prop.name, prop.type)}:\n"
            )

            indent = "    " * (1 + indent_level)
            write_docstring(buffer, prop.doc, indent_level + 1)
            buffer.write(f"{indent}return None\n")
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


# Helper for write_class
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
        method_name = method.Name
        method_return_type = f'{python_type(method_name, fix_str(method.ReturnType.ToString()))}'
        params = method.GetParameters()

        args = []

        for param in params:
            param_type = python_type(method_name, fix_str(param.ParameterType.ToString()))
            if "Ansys." in param_type:
                args.append(Param(type=f'"{param_type}"', name=param.Name))
            else:
                args.append(Param(type=param_type, name=param.Name))

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


# Helper for write_class()
def write_method(buffer: typing.TextIO, method: Method, indent_level: int = 1) -> None:
    # logging.debug(f"        writing method {method.name}")
    indent = "    " * indent_level
    if method.static:
        buffer.write(f"{indent}@classmethod\n")
        first_arg = "cls"
    else:
        first_arg = "self"
    args = [first_arg] + [f'{arg.name}: {arg.type}' for arg in method.args]
    args = f"({', '.join(args)})"
    # def PropertyByAPIName(self, name: "System.String") -> "Ansys.ACT.Automation.Mechanical.Property":
    # """
    #     Get a property by its API name.
    #     If multiple properties have the same API Name, only the first property with that name will be returned.
    # """
    # pass
    buffer.write(f"{indent}def {method.name}{args} -> {method.return_type}:\n")
    indent = "    " * (1 + indent_level)
    write_docstring(buffer, method.doc, indent_level + 1)
    buffer.write(f"{indent}pass\n")
    buffer.write("\n")


#### Make the init files based on the assemblies ####
def make(outdir: str, assembly_name: str, type_filter: typing.Callable = None) -> None:
    """Generate python stubs for an assembly."""
    # logging.info(f"Loading assembly {assembly_name}")
    assembly = clr.AddReference(assembly_name)
    if type_filter is not None:
        logging.info(f"   Using a type_filter: {str(type_filter)}")
    namespaces = get_namespaces(assembly, type_filter)
    dump_types(namespaces)
    doc = get_doc(assembly)
    # logging.info(f"    {len(namespaces.items())} namespaces")
    for namespace, mod_types in namespaces.items():
        # logging.info(f"Processing {namespace}")
        # logging.info(f"   {len(namespaces.items())} namespaces")
        write_module(namespace, mod_types, doc, outdir, type_filter)
        # logging.info(f"Done processing {namespace}")


# def is_namespace(something):
#     """Returns True if object is Namespace: Module"""
#     if isinstance(something, type(System)):
#         return True



# To do:
# property return types
# method arg types whenever it's Ansys.xyz.abc -> have to put it in quotes
#   also have to do the import statements for methods - maybe do that at the
#   same time as the property import statements