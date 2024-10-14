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
"""Test regex in stubs_generator."""

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
