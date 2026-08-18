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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Test that pymechanical stubs provide correct autocomplete / IntelliSense support.

These tests simulate how VS Code (Pylance / pyright) surfaces stub information
to the user.  A failing test means that the corresponding symbol would **not**
appear in VS Code's autocomplete list.

The target Mechanical version is controlled by the ``MECHANICAL_VERSION``
environment variable (e.g. ``252``, ``261``).  All tests fail with an explicit
error message when the variable is not set.
"""

from enum import Enum
import importlib
import json
import os
import shutil
import subprocess
import sys
import textwrap

import pytest

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_STUBS_VERSION: str = os.getenv("MECHANICAL_VERSION", "")


@pytest.fixture(autouse=False)
def require_version():
    """Fail the test if MECHANICAL_VERSION is not set."""
    if not _STUBS_VERSION:
        pytest.fail(
            "MECHANICAL_VERSION environment variable is not set. "
            "Set it to the Mechanical version to test (e.g. MECHANICAL_VERSION=261)."
        )


_ENUMS_MODULE = (
    f"ansys.mechanical.stubs.v{_STUBS_VERSION}.Ansys.Mechanical.DataModel.Enums"
    if _STUBS_VERSION
    else ""
)


def _import_enums():
    """Return the Enums module for the version under test."""
    return importlib.import_module(_ENUMS_MODULE)


def _get_class(name: str):
    """Return a class from the Enums module for the version under test."""
    return getattr(_import_enums(), name)


@pytest.fixture(autouse=False)
def require_contact_type(require_version):
    """Fail the test if ContactType is not present in the stubs."""
    try:
        enums = importlib.import_module(_ENUMS_MODULE)
        if not hasattr(enums, "ContactType"):
            pytest.fail(
                f"ContactType is not present in v{_STUBS_VERSION} stubs. "
                "Ensure the correct version of ansys-mechanical-stubs is installed."
            )
    except ImportError as exc:
        pytest.fail(f"Could not import Enums module for v{_STUBS_VERSION}: {exc}")


def _pyright_available() -> bool:
    """Return True if pyright is reachable on the current PATH / as a module."""
    return shutil.which("pyright") is not None or (
        subprocess.run(
            [sys.executable, "-m", "pyright", "--version"],
            capture_output=True,
        ).returncode
        == 0
    )


# Evaluated once at collection time so the subprocess runs only once per session.
_PYRIGHT_AVAILABLE: bool = _pyright_available()


# ---------------------------------------------------------------------------
# Expected members for ContactType
# ---------------------------------------------------------------------------

_EXPECTED_MEMBERS = {
    "Bonded": 1,
    "Frictional": 3,
    "Frictionless": 2,
    "NoSeparation": 5,
    "Rough": 4,
}


# ===========================================================================
# TestContactType
# ===========================================================================


@pytest.mark.usefixtures("require_version", "require_contact_type")
class TestContactType:
    """Verify that ContactType works as an Enum with full autocomplete.

    VS Code autocomplete works by reading the type stubs.  For an enum class,
    Pylance shows each member as a completion item (e.g. ``.Bonded``, ``.Frictional``).
    This only works when the class actually **inherits from** ``enum.Enum`` and
    its members are defined as class-level integer attributes in the stub.
    """

    # ------------------------------------------------------------------
    # 1. Class hierarchy
    # ------------------------------------------------------------------

    def test_class_is_enum_subclass(self):
        """ContactType must inherit from Enum, not object.

        Pylance only generates enum-member completions for ``enum.Enum``
        subclasses.  If the class base is ``object`` no member completions
        are produced.
        """
        cls = _get_class("ContactType")
        assert issubclass(cls, Enum), (
            f"ContactType bases are {cls.__bases__!r}. "
            "Expected a subclass of enum.Enum. "
            "VS Code autocomplete will not show enum members for plain-object stubs."
        )

    def test_class_is_not_plain_object(self):
        """The class must not be a bare ``object`` subclass.

        This catches the scenario where the stubs file
        contains a second ``class ContactType(object):`` block
        that silently replaces the correct Enum definition.
        """
        cls = _get_class("ContactType")
        assert cls.__bases__ != (object,), (
            "ContactType has only 'object' as its base class. "
            "A duplicate object-based definition is shadowing the Enum definition."
        )

    # ------------------------------------------------------------------
    # 2. Member presence (what VS Code would list as completions)
    # ------------------------------------------------------------------

    def test_all_expected_members_exist(self):
        """Every expected enum member must be present (== VS Code completion items)."""
        cls = _get_class("ContactType")
        actual = {m.name for m in cls}
        missing = set(_EXPECTED_MEMBERS) - actual
        assert not missing, (
            f"Missing members (would not appear in VS Code autocomplete): {missing!r}. "
            f"Present: {actual!r}"
        )

    @pytest.mark.parametrize("name,value", _EXPECTED_MEMBERS.items())
    def test_member_value(self, name, value):
        """Each member must carry the correct integer value."""
        cls = _get_class("ContactType")
        member = cls[name]
        assert member.value == value, f"ContactType.{name} = {member.value!r}, expected {value!r}."

    # ------------------------------------------------------------------
    # 3. Attribute / dir() access (what VS Code actually queries)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("name", _EXPECTED_MEMBERS)
    def test_member_accessible_as_attribute(self, name):
        """Each member must be reachable via ``cls.MemberName`` attribute access.

        This is the primary access pattern for VS Code completions:
        after the user types ``ContactType.`` the IDE calls
        ``dir(cls)`` and ``getattr(cls, name)`` for each suggestion.
        """
        cls = _get_class("ContactType")
        assert hasattr(cls, name), (
            f"ContactType.{name} is not accessible via getattr(). "
            "VS Code would not suggest this completion."
        )

    @pytest.mark.parametrize("name", _EXPECTED_MEMBERS)
    def test_member_in_dir(self, name):
        """Each member name must appear in ``dir(ContactType)``.

        Pylance and other completions engines use ``dir()`` to enumerate the
        available attributes.  Members absent from ``dir()`` are absent from
        autocomplete.
        """
        cls = _get_class("ContactType")
        assert name in dir(cls), (
            f"'{name}' is missing from dir(ContactType). "
            "VS Code would not list it as an autocomplete option."
        )

    def test_no_members_means_shadowed_definition(self):
        """If the enum has zero members the Enum definition has been overwritten.

        This covers the scenario where the ``object``-based class has no members at all,
        so ``list(cls)`` returns an empty list.  This assertion produces an
        explicit, human-readable failure message for that case.
        """
        cls = _get_class("ContactType")
        members = list(cls)
        assert members, (
            "ContactType has no members. "
            "The Enum definition is almost certainly shadowed by a duplicate "
            "object-based class further down in the stubs file. "
            "Check for a second 'class ContactType(object):' block."
        )


# ===========================================================================
# TestEnumAccessViaModuleHierarchy
# ===========================================================================


@pytest.mark.usefixtures("require_version", "require_contact_type")
class TestEnumAccessViaModuleHierarchy:
    """Verify enums are reachable via the full dotted namespace.

    Mechanical scripting uses ``Ansys``-rooted paths directly. For example::

        app.Graphics.ViewOptions.ResultPreference.ExtraModelDisplay = (
            Ansys.Mechanical.DataModel.MechanicalEnums.Graphics.ExtraModelDisplay.NoWireframe
        )

    VS Code resolves these completions by walking the stub package hierarchy
    starting from ``Ansys``.  This test imports the versioned stub package and
    walks the equivalent path (``Ansys → Mechanical → DataModel → Enums``) to
    confirm that every intermediate namespace attribute resolves correctly, which
    is the same traversal Pylance performs when building autocomplete suggestions.
    """

    _NAMESPACE_PATH = ["Ansys", "Mechanical", "DataModel", "Enums"]

    def _walk_to_enums(self):
        """Resolve the Enums namespace through the full generated package tree."""
        module = importlib.import_module(f"ansys.mechanical.stubs.v{_STUBS_VERSION}")
        ns = module
        for part in self._NAMESPACE_PATH:
            ns = getattr(ns, part)
        return ns

    def test_enum_class_reachable_via_full_namespace(self):
        """ContactType must be reachable through the module tree."""
        enums_ns = self._walk_to_enums()
        cls = getattr(enums_ns, "ContactType")
        assert issubclass(cls, Enum), "ContactType reached via full namespace is not an Enum."

    @pytest.mark.parametrize("name", _EXPECTED_MEMBERS)
    def test_enum_member_reachable_via_full_namespace(self, name):
        """Each enum member must be reachable via the full dotted path."""
        enums_ns = self._walk_to_enums()
        cls = getattr(enums_ns, "ContactType")
        assert hasattr(cls, name), (
            f"ContactType.{name} not accessible via full namespace. "
            "VS Code autocomplete would not suggest it."
        )


# ===========================================================================
# TestPyrightTypeChecking
# ===========================================================================

_PYRIGHT_SNIPPET = textwrap.dedent(
    f"""\
    # Type-check snippet: pyright must resolve all members without error.
    from ansys.mechanical.stubs.v{_STUBS_VERSION}.Ansys.Mechanical.DataModel.Enums import (
        ContactType,
    )

    _bonded: ContactType = ContactType.Bonded
    _frictional: ContactType = ContactType.Frictional
    _frictionless: ContactType = ContactType.Frictionless
    _no_sep: ContactType = ContactType.NoSeparation
    _rough: ContactType = ContactType.Rough
    """
)


@pytest.mark.usefixtures("require_version", "require_contact_type")
class TestPyrightTypeChecking:
    """Run pyright over stub-consuming code to confirm VS Code would resolve symbols.

    Pylance (the VS Code Python language server) is built on pyright.  If pyright
    reports errors for a particular attribute access, Pylance will not show that
    attribute as an autocomplete suggestion.
    """

    def test_pyright_resolves_all_members(self, tmp_path):
        """Pyright must report zero errors when accessing all enum members."""
        if not _PYRIGHT_AVAILABLE:
            pytest.fail("pyright is not installed. Install it with: pip install pyright")
        test_file = tmp_path / "check_stubs.py"
        test_file.write_text(_PYRIGHT_SNIPPET, encoding="utf-8")

        # Prefer the module form so it works in virtual environments without
        # pyright on the OS PATH.
        if shutil.which("pyright"):
            cmd = ["pyright", str(test_file), "--outputjson"]
        else:
            cmd = [sys.executable, "-m", "pyright", str(test_file), "--outputjson"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"pyright produced non-JSON output:\n{result.stdout}\n{result.stderr}")

        errors = [d for d in data.get("generalDiagnostics", []) if d.get("severity") == "error"]

        assert not errors, (
            "pyright reported errors — VS Code autocomplete would fail:\n"
            + "\n".join(
                f"  line {d.get('range', {}).get('start', {}).get('line', '?')}: "
                f"[{d.get('rule', 'unknown')}] {d.get('message', '')}"
                for d in errors
            )
        )

    def test_pyright_no_missing_attribute_errors(self, tmp_path):
        """Pyright must not report 'Cannot access attribute' for enum members.

        This is the exact error Pylance emits when a member is missing from the
        stub, which means it would also be absent from autocomplete.
        """
        if not _PYRIGHT_AVAILABLE:
            pytest.fail("pyright is not installed. Install it with: pip install pyright")
        test_file = tmp_path / "check_stubs.py"
        test_file.write_text(_PYRIGHT_SNIPPET, encoding="utf-8")

        if shutil.which("pyright"):
            cmd = ["pyright", str(test_file), "--outputjson"]
        else:
            cmd = [sys.executable, "-m", "pyright", str(test_file), "--outputjson"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"pyright produced non-JSON output:\n{result.stdout}\n{result.stderr}")

        attribute_errors = [
            d
            for d in data.get("generalDiagnostics", [])
            if d.get("severity") == "error"
            and "cannot access attribute" in d.get("message", "").lower()
        ]

        assert not attribute_errors, (
            "pyright reports 'Cannot access attribute' errors — these members "
            "would not appear in VS Code autocomplete:\n"
            + "\n".join(f"  {d.get('message', '')}" for d in attribute_errors)
        )


# ===========================================================================
# TestContactTypeMemberProperties
# ===========================================================================


@pytest.mark.usefixtures("require_version", "require_contact_type")
class TestContactTypeMemberProperties:
    """Test each enum member's .name and .value properties.

    This tests the case where a shadowing object-based class has
    no members, so attribute lookup raises AttributeError and iteration is
    empty. All tests are expected to pass once the duplicate definition is
    removed.
    """

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_name_property(self, attr_name, expected_value):
        """``member.name`` must equal the attribute name used to access it.

        VS Code shows the ``.name`` in hover documentation; if the member is
        not a real Enum member ``.name`` will either raise AttributeError or
        return the wrong string.
        """
        cls = _get_class("ContactType")
        member = getattr(cls, attr_name)
        assert member.name == attr_name, (
            f"ContactType.{attr_name}.name == {member.name!r}, expected {attr_name!r}."
        )

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_value_property(self, attr_name, expected_value):
        """``member.value`` must return the documented integer constant."""
        cls = _get_class("ContactType")
        member = getattr(cls, attr_name)
        assert member.value == expected_value, (
            f"ContactType.{attr_name}.value == {member.value!r}, expected {expected_value!r}."
        )

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_type_is_enum_class(self, attr_name, expected_value):
        """Each member must be an instance of the enum class itself.

        ``isinstance(ContactType.Bonded, ContactType)``
        must be True.  With the object-based stub the members don't exist at
        all, so this fails with AttributeError.
        """
        cls = _get_class("ContactType")
        member = getattr(cls, attr_name)
        assert isinstance(member, cls), (
            f"ContactType.{attr_name} is not an instance of ContactType."
        )

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_is_enum_instance(self, attr_name, expected_value):
        """Each member must be an instance of ``enum.Enum``."""
        cls = _get_class("ContactType")
        member = getattr(cls, attr_name)
        assert isinstance(member, Enum), f"ContactType.{attr_name} is not an enum.Enum instance."

    def test_member_count(self):
        """The class must expose at least the documented number of core members."""
        cls = _get_class("ContactType")
        assert len(cls) >= len(_EXPECTED_MEMBERS), (
            f"Expected at least {len(_EXPECTED_MEMBERS)} members, got {len(cls)}: {[m.name for m in cls]!r}."
        )

    def test_members_dict(self):
        """``__members__`` must map every expected name to its member."""
        cls = _get_class("ContactType")
        missing = set(_EXPECTED_MEMBERS) - set(cls.__members__)
        assert not missing, (
            f"Missing from __members__: {missing!r}. "
            "VS Code completion relies on __members__ for enum documentation."
        )


# ===========================================================================
# TestContactTypeEnumBehavior
# ===========================================================================


@pytest.mark.usefixtures("require_version", "require_contact_type")
class TestContactTypeEnumBehavior:
    """Test Python Enum protocol behaviour for ContactType.

    These cover the runtime semantics that VS Code's IntelliSense depends on:
    lookup by value/name, iteration, comparison, hashing, and string
    representations. This fails when the class is object-based.
    """

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_lookup_by_value(self, attr_name, expected_value):
        """``cls(value)`` must return the correct member.

        This is how code like ``ContactType(1)`` → ``.Bonded``
        works at runtime.  The object-based stub does not support call syntax.
        """
        cls = _get_class("ContactType")
        member = cls(expected_value)
        assert member.name == attr_name, (
            f"cls({expected_value}) returned {member.name!r}, expected {attr_name!r}."
        )

    @pytest.mark.parametrize("attr_name", list(_EXPECTED_MEMBERS))
    def test_lookup_by_name(self, attr_name):
        """``cls[name]`` must return the correct member (subscript access)."""
        cls = _get_class("ContactType")
        member = cls[attr_name]
        assert member.name == attr_name, f"cls[{attr_name!r}] returned {member.name!r}."

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def test_iteration_yields_all_members(self):
        """``for m in cls`` must yield every expected member exactly once."""
        cls = _get_class("ContactType")
        names = {m.name for m in cls}
        assert set(_EXPECTED_MEMBERS).issubset(names), (
            f"Expected members {set(_EXPECTED_MEMBERS)!r} not all present; got {names!r}."
        )

    def test_iteration_yields_enum_instances(self):
        """Every object yielded by iteration must be an Enum instance."""
        cls = _get_class("ContactType")
        for member in cls:
            assert isinstance(member, Enum), f"Iteration yielded non-Enum object: {member!r}."

    # ------------------------------------------------------------------
    # Comparison and identity
    # ------------------------------------------------------------------

    def test_same_member_equality(self):
        """A member must equal itself (``Bonded == Bonded``)."""
        cls = _get_class("ContactType")
        assert cls.Bonded == cls.Bonded

    def test_different_members_inequality(self):
        """Different members must not be equal (``Bonded != Frictional``)."""
        cls = _get_class("ContactType")
        assert cls.Bonded != cls.Frictional

    def test_member_identity(self):
        """Accessing the same member twice must return the identical object."""
        cls = _get_class("ContactType")
        assert cls.Bonded is cls.Bonded

    def test_member_not_equal_to_raw_value(self):
        """An enum member must not compare equal to its raw integer value.

        Python Enum members are NOT equal to plain ints (unless IntEnum is
        used).  This verifies the class really is Enum-based, not int-based.
        """
        cls = _get_class("ContactType")
        assert cls.Bonded != 1, (
            "ContactType.Bonded == 1 — the class may be IntEnum "
            "or the value is leaking as a plain int."
        )

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def test_members_are_hashable(self):
        """Enum members must be hashable (usable as dict keys / set members)."""
        cls = _get_class("ContactType")
        member_set = set(cls)
        assert len(member_set) == len(list(cls)), (
            "Not all members could be added to a set — hashing is broken."
        )

    def test_member_as_dict_key(self):
        """Enum members must work as dict keys."""
        cls = _get_class("ContactType")
        mapping = {m: m.value for m in cls}
        assert mapping[cls.Bonded] == 1

    def test_member_in_set(self):
        """``cls.Bonded in {cls.Bonded, cls.Frictional}`` must be True."""
        cls = _get_class("ContactType")
        s = {cls.Bonded, cls.Frictional}
        assert cls.Bonded in s
        assert cls.Frictionless not in s

    # ------------------------------------------------------------------
    # String representations
    # ------------------------------------------------------------------

    def test_str_includes_member_name(self):
        """``str(member)`` must include the member name for hover documentation."""
        cls = _get_class("ContactType")
        s = str(cls.Bonded)
        assert "Bonded" in s, f"str(ContactType.Bonded) == {s!r} does not contain 'Bonded'."

    def test_repr_includes_class_and_member(self):
        """``repr(member)`` should include both the class and the member name."""
        cls = _get_class("ContactType")
        r = repr(cls.Bonded)
        assert "Bonded" in r, f"repr contains no member name: {r!r}."
        assert "ContactType" in r, f"repr contains no class name: {r!r}."

    # ------------------------------------------------------------------
    # Containment
    # ------------------------------------------------------------------

    def test_member_containment(self):
        """``cls.Bonded in cls`` must be True."""
        cls = _get_class("ContactType")
        assert cls.Bonded in cls

    def test_non_member_not_contained(self):
        """A random integer must not be reported as contained in the enum."""
        cls = _get_class("ContactType")
        assert all(member.value != 999 for member in cls), (
            "Unexpected enum member with value 999 found in ContactType."
        )

    # ------------------------------------------------------------------
    # Docstring
    # ------------------------------------------------------------------

    def test_class_has_docstring(self):
        """The class must have a docstring (VS Code shows this in hover tips)."""
        cls = _get_class("ContactType")
        assert cls.__doc__, (
            "ContactType has no docstring. VS Code hover documentation will be empty."
        )


# ===========================================================================
# TestContactTypeNetMethods
# ===========================================================================


@pytest.mark.usefixtures("require_version", "require_contact_type")
class TestContactTypeNetMethods:
    """.NET System.Enum methods must be present on ContactType.

    Every .NET enum inherits from System.Enum, which provides CompareTo,
    HasFlag, and GetTypeCode.  Methods inherited from System.Object
    (GetHashCode, ToString, Equals, GetType) are intentionally excluded from
    the generated stubs because they are noise that adds no value for
    Mechanical scripting users.

    The stubs must expose the System.Enum-declared methods so VS Code
    autocomplete shows them when a user types ``my_method_value.<TAB>``.
    """

    _NET_METHODS = [
        "CompareTo",
        "HasFlag",
        "GetTypeCode",
    ]

    @pytest.mark.parametrize("method_name", _NET_METHODS)
    def test_net_method_present(self, method_name):
        """Each .NET-inherited method must be accessible on the class.

        Pylance surfaces these in the member-completion list when the user
        types ``ContactType.Bonded.<TAB>``.
        """
        cls = _get_class("ContactType")
        assert hasattr(cls, method_name), (
            f"ContactType is missing the .NET method '{method_name}'. "
            "VS Code would not suggest it as a completion on enum instances."
        )

    @pytest.mark.parametrize("method_name", _NET_METHODS)
    def test_net_method_is_callable(self, method_name):
        """Each .NET-inherited method must be callable (not just an attribute)."""
        cls = _get_class("ContactType")
        method = getattr(cls, method_name)
        assert callable(method), f"ContactType.{method_name} is not callable."

    def test_class_is_still_enum_with_net_methods(self):
        """Having .NET methods must not prevent the class from being an Enum.

        The fix merges .NET methods INTO the Enum-based class, so both enum
        membership and .NET method access work simultaneously.
        """
        cls = _get_class("ContactType")
        assert issubclass(cls, Enum), (
            "ContactType lost its Enum base after .NET methods "
            "were added.  The class must inherit from both Enum and expose the "
            ".NET methods."
        )

    def test_enum_members_survive_net_methods(self):
        """Enum members must still be present alongside the .NET methods."""
        cls = _get_class("ContactType")
        for name in _EXPECTED_MEMBERS:
            assert hasattr(cls, name), f"Member '{name}' disappeared after .NET methods were added."


# ===========================================================================
# TestWorkingEnumControl  (reference enums that should always pass)
# ===========================================================================


@pytest.mark.usefixtures("require_version")
class TestWorkingEnumControl:
    """Sanity-check enums that do NOT have a duplicate object-based definition.

    These tests must always pass.  If they fail the test infrastructure itself
    is broken (wrong package installed, import error, etc.).

    ``AutomaticOrManual`` and ``AutomaticTimeStepping`` are simple two/three-
    member enums with no duplicate in the stubs file.
    """

    # -----------------------------------------------------------------------
    # AutomaticOrManual  (Automatic=1, Manual=0)
    # -----------------------------------------------------------------------

    def test_automatic_or_manual_is_enum(self):
        """AutomaticOrManual must remain a plain, working Enum."""
        cls = _get_class("AutomaticOrManual")
        assert issubclass(cls, Enum)

    @pytest.mark.parametrize("name,value", [("Automatic", 1), ("Manual", 0)])
    def test_automatic_or_manual_members(self, name, value):
        """AutomaticOrManual members must expose the documented names and values."""
        cls = _get_class("AutomaticOrManual")
        member = getattr(cls, name)
        assert member.name == name
        assert member.value == value

    def test_automatic_or_manual_lookup_by_value(self):
        """AutomaticOrManual must support Enum lookup by integer value."""
        cls = _get_class("AutomaticOrManual")
        assert cls(1).name == "Automatic"
        assert cls(0).name == "Manual"

    def test_automatic_or_manual_equality(self):
        """AutomaticOrManual members must compare equal only to themselves."""
        cls = _get_class("AutomaticOrManual")
        assert cls.Automatic == cls.Automatic
        assert cls.Automatic != cls.Manual

    def test_automatic_or_manual_hash(self):
        """AutomaticOrManual members must be hashable for set usage."""
        cls = _get_class("AutomaticOrManual")
        assert {cls.Automatic, cls.Manual} == {cls.Manual, cls.Automatic}

    # -----------------------------------------------------------------------
    # AutomaticTimeStepping  (Off=2, On=1, ProgramControlled=0)
    # -----------------------------------------------------------------------

    def test_automatic_time_stepping_is_enum(self):
        """AutomaticTimeStepping must remain a plain, working Enum."""
        cls = _get_class("AutomaticTimeStepping")
        assert issubclass(cls, Enum)

    @pytest.mark.parametrize("name,value", [("Off", 2), ("On", 1), ("ProgramControlled", 0)])
    def test_automatic_time_stepping_members(self, name, value):
        """AutomaticTimeStepping members must expose the documented names and values."""
        cls = _get_class("AutomaticTimeStepping")
        member = getattr(cls, name)
        assert member.name == name
        assert member.value == value

    def test_automatic_time_stepping_iteration_count(self):
        """AutomaticTimeStepping must expose exactly three members."""
        cls = _get_class("AutomaticTimeStepping")
        assert len(cls) == 3

    def test_automatic_time_stepping_member_types(self):
        """AutomaticTimeStepping iteration must yield Enum instances of its own type."""
        cls = _get_class("AutomaticTimeStepping")
        for m in cls:
            assert isinstance(m, cls)
            assert isinstance(m, Enum)

    def test_automatic_time_stepping_lookup_by_name(self):
        """AutomaticTimeStepping must support Enum lookup by member name."""
        cls = _get_class("AutomaticTimeStepping")
        assert cls["ProgramControlled"].value == 0

    def test_automatic_time_stepping_containment(self):
        """AutomaticTimeStepping must contain its members and exclude unknown values."""
        cls = _get_class("AutomaticTimeStepping")
        assert cls.Off in cls
        assert all(member.value != 999 for member in cls), (
            "Unexpected enum member with value 999 found in AutomaticTimeStepping."
        )

    def test_automatic_time_stepping_str(self):
        """AutomaticTimeStepping string form must include the member name."""
        cls = _get_class("AutomaticTimeStepping")
        assert "Off" in str(cls.Off)

    def test_automatic_time_stepping_repr(self):
        """AutomaticTimeStepping repr must include both class and member names."""
        cls = _get_class("AutomaticTimeStepping")
        r = repr(cls.Off)
        assert "Off" in r
        assert "AutomaticTimeStepping" in r

    # -----------------------------------------------------------------------
    # AxisSelectionType  (All=0, XAxis=1, YAxis=2, ZAxis=3)
    # -----------------------------------------------------------------------

    _AXIS_MEMBERS = {"All": 0, "XAxis": 1, "YAxis": 2, "ZAxis": 3}

    def test_axis_selection_type_is_enum(self):
        """AxisSelectionType must remain a plain, working Enum."""
        cls = _get_class("AxisSelectionType")
        assert issubclass(cls, Enum)

    @pytest.mark.parametrize("name,value", list(_AXIS_MEMBERS.items()))
    def test_axis_selection_type_members(self, name, value):
        """AxisSelectionType members must expose the documented names and values."""
        cls = _get_class("AxisSelectionType")
        member = getattr(cls, name)
        assert member.name == name
        assert member.value == value

    def test_axis_selection_type_member_count(self):
        """AxisSelectionType must expose exactly four members."""
        cls = _get_class("AxisSelectionType")
        assert len(cls) == 4

    def test_axis_selection_type_members_dict(self):
        """AxisSelectionType.__members__ must contain all expected names."""
        cls = _get_class("AxisSelectionType")
        assert set(cls.__members__) == set(self._AXIS_MEMBERS)

    def test_axis_selection_type_hashable_and_set(self):
        """AxisSelectionType members must be hashable for set usage."""
        cls = _get_class("AxisSelectionType")
        assert len({m for m in cls}) == 4

    def test_axis_selection_type_dict_key(self):
        """AxisSelectionType members must work as dictionary keys."""
        cls = _get_class("AxisSelectionType")
        d = {cls.XAxis: "x", cls.YAxis: "y"}
        assert d[cls.XAxis] == "x"

    # -----------------------------------------------------------------------
    # BaseResultType  (multi-member; spot-check a few)
    # -----------------------------------------------------------------------

    _BASE_RESULT_SPOT = {"Mass": 5, "Displacement": 0}

    def test_base_result_type_is_enum(self):
        """BaseResultType must remain a plain, working Enum."""
        cls = _get_class("BaseResultType")
        assert issubclass(cls, Enum)

    @pytest.mark.parametrize("name,value", list(_BASE_RESULT_SPOT.items()))
    def test_base_result_type_member_values(self, name, value):
        """BaseResultType spot-check values must match the generated stub."""
        cls = _get_class("BaseResultType")
        assert cls[name].value == value


# ===========================================================================
# TestEnumModuleExports
# ===========================================================================


@pytest.mark.usefixtures("require_version")
class TestAllEnumsHaveMembers:
    """Verify that every Enum class in the Enums module has at least one member.

    This is a broad generator-correctness check: if any enum ends up with zero
    members it means the stub generator's type_filter was incorrectly applied to
    enum field constants, or a duplicate ``object``-based class shadowed the
    ``Enum``-based one.  Both failure modes make VS Code autocomplete show no
    completion items for that enum.
    """

    def test_all_enum_classes_have_members(self):
        """Every Enum subclass in the Enums module must have at least one member."""
        import inspect

        enums_module = _import_enums()

        enum_classes = [
            (name, getattr(enums_module, name))
            for name in dir(enums_module)
            if inspect.isclass(getattr(enums_module, name, None))
            and issubclass(getattr(enums_module, name), Enum)
            and getattr(enums_module, name) is not Enum
        ]

        assert len(enum_classes) > 0, (
            f"No Enum classes found in {_ENUMS_MODULE}. "
            "The module may not have been generated correctly."
        )

        empty = [name for name, cls in enum_classes if len(list(cls)) == 0]
        assert not empty, (
            f"The following enums in {_ENUMS_MODULE} have no members "
            "(would show empty autocomplete lists in VS Code):\n  "
            + "\n  ".join(empty)
            + "\nCheck that type_filter is not applied to enum field constants "
            "in the stub generator, and that no object-based duplicate class "
            "shadows the Enum-based definition."
        )


# ===========================================================================
# TestEnumModuleExports
# ===========================================================================


@pytest.mark.usefixtures("require_version")
class TestEnumModuleExports:
    """Verify the Enums module exports all classes needed for VS Code autocomplete.

    The module-level ``dir()`` is what Pylance uses to build the completion
    list for ``from ansys...Enums import <TAB>``.  A class absent from
    ``dir(module)`` will not appear in that completion list.
    """

    _EXPECTED_EXPORTS = [
        "ContactType",
        "AutomaticOrManual",
        "AutomaticTimeStepping",
        "AxisSelectionType",
        "BaseResultType",
        "BeamBeamModel",
        "BeamEndReleaseBehavior",
        "BeamOffsetType",
    ]

    @pytest.mark.parametrize("class_name", _EXPECTED_EXPORTS)
    def test_class_in_module_dir(self, class_name):
        """Each expected class must appear in ``dir(enums_module)``."""
        module = _import_enums()
        assert class_name in dir(module), (
            f"'{class_name}' is missing from dir(Enums module). "
            "Pylance would not suggest it in import completions."
        )

    @pytest.mark.parametrize("class_name", _EXPECTED_EXPORTS)
    def test_class_importable(self, class_name):
        """Each class must be importable directly from the Enums module."""
        module = _import_enums()
        cls = getattr(module, class_name, None)
        assert cls is not None, f"Cannot import '{class_name}' from the Enums module."
        assert isinstance(cls, type), f"'{class_name}' is not a type/class object: {cls!r}."
