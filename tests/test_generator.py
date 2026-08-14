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

"""Tests for the stub generator (generate_content.py).

Covers:
- C# --> Python type-string conversion (c_types_to_python)
- CLR method overload grouping and emission (write_method_group)
"""

import io

import pytest

from ansys.mechanical.stubs.stub_generator.generate_content import (
    Method,
    Param,
    c_types_to_python,
    write_method_group,
)

_SYSTEM_FUNC_TYPE = (
    "System.Func[Ansys.Mechanical.DataModel.Interfaces.IDataModelObject,System.Boolean]"
)
_EXPECTED_SYSTEM_FUNC_TYPE = (
    '"System.Func[Ansys.Mechanical.DataModel.Interfaces.IDataModelObject,bool]"'
)
_GENERIC_ENUMERABLE_OF_KV_ENUMERABLE = (
    "System.Collections.Generic.IEnumerable["
    "System.Collections.Generic.KeyValuePair["
    "System.Int32,"
    "System.Collections.Generic.IEnumerable[Ansys.Core.Units.Quantity]]]"
)


_TYPE_CONVERSION_CASES = [
    # Namespaced Ansys interface should remain unchanged.
    (
        "Ansys.ACT.Interfaces.Mechanical.IParameter",
        "Ansys.ACT.Interfaces.Mechanical.IParameter",
    ),
    # Generic .NET IList should map to typing.List with the same type argument.
    (
        "System.Collections.Generic.IList[ChildrenType]",
        "typing.List[ChildrenType]",
    ),
    # System.Func is intentionally preserved as a quoted type string.
    (_SYSTEM_FUNC_TYPE, _EXPECTED_SYSTEM_FUNC_TYPE),
    # This is a single long input string split across literals for readability.
    # Nested IEnumerable<KeyValuePair<int, IEnumerable<T>>> should map recursively.
    (
        _GENERIC_ENUMERABLE_OF_KV_ENUMERABLE,
        "typing.Iterable[dict[int,typing.Iterable[Ansys.Core.Units.Quantity]]]",
    ),
    # Quoted .NET Tuple annotation should convert to Python tuple[type1, type2].
    (
        '"System.Tuple[Ansys.Core.Units.Quantity,Ansys.Core.Units.Quantity]"',
        "tuple[Ansys.Core.Units.Quantity,Ansys.Core.Units.Quantity]",
    ),
    # IronPython runtime tuple type should collapse to plain Python tuple.
    (
        '"IronPython.Runtime.PythonTuple"',
        "tuple",
    ),
]


@pytest.mark.parametrize("cs_type,expected_py_type", _TYPE_CONVERSION_CASES)
def test_c_type_to_python(cs_type, expected_py_type):
    """Each C# type string must convert to the expected Python type annotation."""
    assert c_types_to_python(cs_type) == expected_py_type


# ===========================================================================
# write_method_group — overload emission
# ===========================================================================


def test_write_method_group_emits_overloads_and_single_implementation():
    """Repeated CLR methods should emit @typing.overload stubs plus one broad implementation."""
    buffer = io.StringIO()
    methods = [
        Method(name="ToString", doc=None, return_type='"System.String"', static=False, args=[]),
        Method(
            name="ToString",
            doc=None,
            return_type='"System.String"',
            static=False,
            args=[Param(type='"System.String"', name="format")],
        ),
    ]

    write_method_group(buffer, methods)
    contents = buffer.getvalue()

    assert contents.count("@typing.overload") == 2
    assert contents.count("def ToString(") == 3
    assert "def ToString(self) -> str:\n        ..." in contents
    assert "def ToString(self, format: str) -> str:\n        ..." in contents
    assert 'def ToString(self, *args: typing.Any) -> str:\n        """\n' in contents


def test_write_method_group_single_method_emits_no_overload():
    """A method with only one CLR signature must not emit any @typing.overload."""
    buffer = io.StringIO()
    methods = [
        Method(name="GetType", doc=None, return_type='"System.Type"', static=False, args=[]),
    ]

    write_method_group(buffer, methods)
    contents = buffer.getvalue()

    assert "@typing.overload" not in contents
    assert contents.count("def GetType(") == 1
    assert "*args" not in contents


def test_write_method_group_keeps_classmethod_on_overloads_and_implementation():
    """Static CLR overloads should emit @classmethod on every generated signature."""
    buffer = io.StringIO()
    methods = [
        Method(
            name="Parse",
            doc=None,
            return_type='"System.Int32"',
            static=True,
            args=[Param(type='"System.String"', name="value")],
        ),
        Method(
            name="Parse",
            doc=None,
            return_type='"System.Int32"',
            static=True,
            args=[
                Param(type='"System.String"', name="value"),
                Param(type='"System.IFormatProvider"', name="provider"),
            ],
        ),
    ]

    write_method_group(buffer, methods)
    contents = buffer.getvalue()

    assert contents.count("@classmethod") == 3
    assert contents.count("@typing.overload") == 2
    assert "def Parse(cls, value: str) -> int:\n        ..." in contents
    assert "def Parse(cls, *args: typing.Any) -> int:\n        " in contents


def test_write_method_group_mixed_return_types_use_union():
    """Overloads with different return types should use a union in the implementation."""
    buffer = io.StringIO()
    methods = [
        Method(name="Convert", doc=None, return_type='"System.String"', static=False, args=[]),
        Method(
            name="Convert",
            doc=None,
            return_type='"System.Int32"',
            static=False,
            args=[Param(type='"System.Int32"', name="radix")],
        ),
    ]

    write_method_group(buffer, methods)
    contents = buffer.getvalue()

    # Each @typing.overload keeps its specific return type
    assert "def Convert(self) -> str:" in contents
    assert "def Convert(self, radix: int) -> int:" in contents
    # Final implementation combines differing return types into a union
    assert "def Convert(self, *args: typing.Any) -> str | int:" in contents
