# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Test regex in stubs_generator."""

from enum import Enum
import importlib
import inspect
import os

from ansys.mechanical.stubs.stub_generator.generate_content import c_types_to_python


def test_regex():
    """Test the C# types are correctly changed to Python."""
    # Types to test
    test_types = {
        "Ansys.ACT.Interfaces.Mechanical.IParameter": '"Ansys.ACT.Interfaces.Mechanical.IParameter"',
        "System.Collections.Generic.IList[ChildrenType]": 'list["ChildrenType"]',
        "System.Func[Ansys.Mechanical.DataModel.Interfaces.IDataModelObject,System.Boolean]": '"System.Func[Ansys.Mechanical.DataModel.Interfaces.IDataModelObject,bool]"',
        "System.Collections.Generic.IEnumerable[System.Collections.Generic.KeyValuePair[System.Int32,System.Collections.Generic.IEnumerable[Ansys.Core.Units.Quantity]]]": 'typing.Iterable[dict[int,typing.Iterable["Ansys.Core.Units.Quantity"]]]',
        '"System.Tuple[Ansys.Core.Units.Quantity,Ansys.Core.Units.Quantity]"': 'tuple["Ansys.Core.Units.Quantity","Ansys.Core.Units.Quantity"]',
        '"IronPython.Runtime.PythonTuple"': "tuple",
    }

    # Assert that the key is equal to the value
    for key, value in test_types.items():
        assert c_types_to_python(key) == value


def test_enums_have_values():
    """Verify that generated enum classes have values (not just 'pass').

    Tests the mechanical version specified in the MECHANICAL_VERSION environment
    variable. Skips if the variable is not set.
    """
    mech_version = os.getenv("MECHANICAL_VERSION")
    if mech_version is None:
        import pytest

        pytest.fail("MECHANICAL_VERSION environment variable not set")

    module_path = f"ansys.mechanical.stubs.v{mech_version}.Ansys.Mechanical.DataModel.Enums"

    try:
        enums = importlib.import_module(module_path)
    except ImportError as e:
        # Stubs may not be installed in all test environments
        print(f"Could not import {module_path}: {e}")
        return

    # Collect all Enum classes from the module
    enum_classes = []
    for name in dir(enums):
        obj = getattr(enums, name)
        try:
            if inspect.isclass(obj) and issubclass(obj, Enum) and obj is not Enum:
                enum_classes.append((name, obj))
        except TypeError:
            # Some objects might not be classes
            pass

    # Validate that each enum has at least one member
    assert len(enum_classes) > 0, f"No Enum classes found in {module_path}"

    for enum_name, enum_class in enum_classes:
        members = list(enum_class)
        assert len(members) > 0, (
            f"Enum '{enum_name}' in {module_path} has no members. This indicates "
            f"the enum values were not generated. Check that type_filter is not "
            f"incorrectly applied to enum field constants in stub generation."
        )
