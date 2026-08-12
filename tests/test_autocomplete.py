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
environment variable (e.g. ``252``, ``261``).  All tests are skipped when the
variable is not set.

Known-broken symbol in v0.1.14
-------------------------------
``Ansys.Mechanical.DataModel.Enums.AutomaticNodeMovementMethod``

The stubs file contains **two** class definitions with the same name.  Python
uses the last definition, which is an ``object``-based stub that has no enum
members.  The earlier ``Enum``-based definition (with Aggressive / Conservative /
Custom / Off / ProgramControlled) is silently discarded.

All tests in ``TestAutomaticNodeMovementMethod`` are therefore expected to
**fail** until the duplicate class definition is removed.
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

_skip_no_version = pytest.mark.skipif(
    not _STUBS_VERSION,
    reason="MECHANICAL_VERSION environment variable not set — skipping autocomplete tests.",
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


def _enum_class_exists(name: str) -> bool:
    """Return True when *name* exists in the Enums module for the current version."""
    if not _STUBS_VERSION:
        return False
    try:
        return hasattr(_import_enums(), name)
    except Exception:
        return False


_skip_no_anmm = pytest.mark.skipif(
    not _enum_class_exists("AutomaticNodeMovementMethod"),
    reason=(
        f"AutomaticNodeMovementMethod not present in v{_STUBS_VERSION} stubs "
        "— skipping version-specific tests."
    ),
)


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
# Expected members for AutomaticNodeMovementMethod
# ---------------------------------------------------------------------------

_EXPECTED_MEMBERS = {
    "Aggressive": 3,
    "Conservative": 2,
    "Custom": 4,
    "Off": 0,
    "ProgramControlled": 1,
}


# ===========================================================================
# TestAutomaticNodeMovementMethod
# ===========================================================================


@_skip_no_version
@_skip_no_anmm
class TestAutomaticNodeMovementMethod:
    """Verify that AutomaticNodeMovementMethod works as an Enum with full autocomplete.

    VS Code autocomplete works by reading the type stubs.  For an enum class,
    Pylance shows each member as a completion item (e.g. ``.Off``, ``.Aggressive``).
    This only works when the class actually **inherits from** ``enum.Enum`` and
    its members are defined as class-level integer attributes in the stub.

    In v0.1.14 the stubs generator emits a second class block with the same name
    but using ``object`` as the base class.  Python's module loader overwrites the
    correct ``Enum`` definition with this bare-object version, so the members
    disappear entirely—both at runtime and in static analysis tools like pyright.

    All tests below are expected to **FAIL** against v0.1.14 and should pass
    once the duplicate definition is fixed.
    """

    # ------------------------------------------------------------------
    # 1. Class hierarchy
    # ------------------------------------------------------------------

    def test_class_is_enum_subclass(self):
        """AutomaticNodeMovementMethod must inherit from Enum, not object.

        Pylance only generates enum-member completions for ``enum.Enum``
        subclasses.  If the class base is ``object`` no member completions
        are produced.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert issubclass(cls, Enum), (
            f"AutomaticNodeMovementMethod bases are {cls.__bases__!r}. "
            "Expected a subclass of enum.Enum. "
            "VS Code autocomplete will not show enum members for plain-object stubs."
        )

    def test_class_is_not_plain_object(self):
        """The class must not be a bare ``object`` subclass.

        This specifically catches the v0.1.14 regression where the stubs file
        contains a second ``class AutomaticNodeMovementMethod(object):`` block
        that silently replaces the correct Enum definition.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.__bases__ != (object,), (
            "AutomaticNodeMovementMethod has only 'object' as its base class. "
            "A duplicate object-based definition is shadowing the Enum definition."
        )

    # ------------------------------------------------------------------
    # 2. Member presence (what VS Code would list as completions)
    # ------------------------------------------------------------------

    def test_all_expected_members_exist(self):
        """Every expected enum member must be present (== VS Code completion items)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        actual = {m.name for m in cls}
        missing = set(_EXPECTED_MEMBERS) - actual
        assert not missing, (
            f"Missing members (would not appear in VS Code autocomplete): {missing!r}. "
            f"Present: {actual!r}"
        )

    @pytest.mark.parametrize("name,value", _EXPECTED_MEMBERS.items())
    def test_member_value(self, name, value):
        """Each member must carry the correct integer value."""
        cls = _get_class("AutomaticNodeMovementMethod")
        member = cls[name]
        assert member.value == value, (
            f"AutomaticNodeMovementMethod.{name} = {member.value!r}, expected {value!r}."
        )

    # ------------------------------------------------------------------
    # 3. Attribute / dir() access (what VS Code actually queries)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("name", _EXPECTED_MEMBERS)
    def test_member_accessible_as_attribute(self, name):
        """Each member must be reachable via ``cls.MemberName`` attribute access.

        This is the primary access pattern for VS Code completions:
        after the user types ``AutomaticNodeMovementMethod.`` the IDE calls
        ``dir(cls)`` and ``getattr(cls, name)`` for each suggestion.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert hasattr(cls, name), (
            f"AutomaticNodeMovementMethod.{name} is not accessible via getattr(). "
            "VS Code would not suggest this completion."
        )

    @pytest.mark.parametrize("name", _EXPECTED_MEMBERS)
    def test_member_in_dir(self, name):
        """Each member name must appear in ``dir(AutomaticNodeMovementMethod)``.

        Pylance and other completions engines use ``dir()`` to enumerate the
        available attributes.  Members absent from ``dir()`` are absent from
        autocomplete.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert name in dir(cls), (
            f"'{name}' is missing from dir(AutomaticNodeMovementMethod). "
            "VS Code would not list it as an autocomplete option."
        )

    def test_no_members_means_shadowed_definition(self):
        """If the enum has zero members the Enum definition has been overwritten.

        In the v0.1.14 bug the ``object``-based class has no members at all,
        so ``list(cls)`` returns an empty list.  This assertion produces an
        explicit, human-readable failure message for that case.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        members = list(cls)
        assert members, (
            "AutomaticNodeMovementMethod has no members. "
            "The Enum definition is almost certainly shadowed by a duplicate "
            "object-based class further down in the stubs file. "
            "Check for a second 'class AutomaticNodeMovementMethod(object):' block."
        )


# ===========================================================================
# TestEnumAccessViaModuleHierarchy
# ===========================================================================


@_skip_no_version
@_skip_no_anmm
class TestEnumAccessViaModuleHierarchy:
    """Verify enums are reachable via the full dotted namespace.

    A user working in VS Code typically does::

        import ansys.mechanical.stubs.v<version> as mech

    and then accesses enums as::

        mech.Ansys.Mechanical.DataModel.Enums.AutomaticNodeMovementMethod.Off

    This test walks that exact dotted path to confirm each step resolves.
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
        """AutomaticNodeMovementMethod must be reachable through the module tree."""
        enums_ns = self._walk_to_enums()
        cls = getattr(enums_ns, "AutomaticNodeMovementMethod")
        assert issubclass(cls, Enum), (
            "AutomaticNodeMovementMethod reached via full namespace is not an Enum."
        )

    @pytest.mark.parametrize("name", _EXPECTED_MEMBERS)
    def test_enum_member_reachable_via_full_namespace(self, name):
        """Each enum member must be reachable via the full dotted path."""
        enums_ns = self._walk_to_enums()
        cls = getattr(enums_ns, "AutomaticNodeMovementMethod")
        assert hasattr(cls, name), (
            f"AutomaticNodeMovementMethod.{name} not accessible via full namespace. "
            "VS Code autocomplete would not suggest it."
        )


# ===========================================================================
# TestPyrightTypeChecking
# ===========================================================================

_PYRIGHT_SNIPPET = textwrap.dedent(
    f"""\
    # Type-check snippet: pyright must resolve all members without error.
    from ansys.mechanical.stubs.v{_STUBS_VERSION}.Ansys.Mechanical.DataModel.Enums import (
        AutomaticNodeMovementMethod,
    )

    _off: AutomaticNodeMovementMethod = AutomaticNodeMovementMethod.Off
    _aggressive: AutomaticNodeMovementMethod = AutomaticNodeMovementMethod.Aggressive
    _conservative: AutomaticNodeMovementMethod = AutomaticNodeMovementMethod.Conservative
    _custom: AutomaticNodeMovementMethod = AutomaticNodeMovementMethod.Custom
    _pc: AutomaticNodeMovementMethod = AutomaticNodeMovementMethod.ProgramControlled
    """
)


@_skip_no_version
@_skip_no_anmm
class TestPyrightTypeChecking:
    """Run pyright over stub-consuming code to confirm VS Code would resolve symbols.

    Pylance (the VS Code Python language server) is built on pyright.  If pyright
    reports errors for a particular attribute access, Pylance will not show that
    attribute as an autocomplete suggestion.

    These tests are skipped automatically when pyright is not installed.
    Install it with::

        pip install pyright
    """

    @pytest.mark.skipif(not _PYRIGHT_AVAILABLE, reason="pyright not installed")
    def test_pyright_resolves_all_members(self, tmp_path):
        """Pyright must report zero errors when accessing all enum members."""
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

    @pytest.mark.skipif(not _PYRIGHT_AVAILABLE, reason="pyright not installed")
    def test_pyright_no_missing_attribute_errors(self, tmp_path):
        """Pyright must not report 'Cannot access attribute' for enum members.

        This is the exact error Pylance emits when a member is missing from the
        stub, which means it would also be absent from autocomplete.
        """
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
# TestAutomaticNodeMovementMethodMemberProperties
# ===========================================================================


@_skip_no_version
@_skip_no_anmm
class TestAutomaticNodeMovementMethodMemberProperties:
    """Test each enum member's .name and .value properties.

    These tests fail in v0.1.14 because the shadowing object-based class has
    no members, so attribute lookup raises AttributeError and iteration is
    empty.  All tests are expected to pass once the duplicate definition is
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
        cls = _get_class("AutomaticNodeMovementMethod")
        member = getattr(cls, attr_name)
        assert member.name == attr_name, (
            f"AutomaticNodeMovementMethod.{attr_name}.name == {member.name!r}, "
            f"expected {attr_name!r}."
        )

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_value_property(self, attr_name, expected_value):
        """``member.value`` must return the documented integer constant."""
        cls = _get_class("AutomaticNodeMovementMethod")
        member = getattr(cls, attr_name)
        assert member.value == expected_value, (
            f"AutomaticNodeMovementMethod.{attr_name}.value == {member.value!r}, "
            f"expected {expected_value!r}."
        )

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_type_is_enum_class(self, attr_name, expected_value):
        """Each member must be an instance of the enum class itself.

        ``isinstance(AutomaticNodeMovementMethod.Off, AutomaticNodeMovementMethod)``
        must be True.  With the object-based stub the members don't exist at
        all, so this fails with AttributeError.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        member = getattr(cls, attr_name)
        assert isinstance(member, cls), (
            f"AutomaticNodeMovementMethod.{attr_name} is not an instance of "
            "AutomaticNodeMovementMethod."
        )

    @pytest.mark.parametrize(
        "attr_name, expected_value",
        list(_EXPECTED_MEMBERS.items()),
    )
    def test_member_is_enum_instance(self, attr_name, expected_value):
        """Each member must be an instance of ``enum.Enum``."""
        cls = _get_class("AutomaticNodeMovementMethod")
        member = getattr(cls, attr_name)
        assert isinstance(member, Enum), (
            f"AutomaticNodeMovementMethod.{attr_name} is not an enum.Enum instance."
        )

    def test_member_count(self):
        """The class must expose exactly the documented number of members."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert len(cls) == len(_EXPECTED_MEMBERS), (
            f"Expected {len(_EXPECTED_MEMBERS)} members, got {len(cls)}: {[m.name for m in cls]!r}."
        )

    def test_members_dict(self):
        """``__members__`` must map every expected name to its member."""
        cls = _get_class("AutomaticNodeMovementMethod")
        missing = set(_EXPECTED_MEMBERS) - set(cls.__members__)
        assert not missing, (
            f"Missing from __members__: {missing!r}. "
            "VS Code completion relies on __members__ for enum documentation."
        )


# ===========================================================================
# TestAutomaticNodeMovementMethodEnumBehavior
# ===========================================================================


@_skip_no_version
@_skip_no_anmm
class TestAutomaticNodeMovementMethodEnumBehavior:
    """Test Python Enum protocol behaviour for AutomaticNodeMovementMethod.

    These cover the runtime semantics that VS Code's IntelliSense depends on:
    lookup by value/name, iteration, comparison, hashing, and string
    representations.  All fail in v0.1.14 where the class is object-based.
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

        This is how code like ``AutomaticNodeMovementMethod(0)`` → ``.Off``
        works at runtime.  The object-based stub does not support call syntax.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        member = cls(expected_value)
        assert member.name == attr_name, (
            f"cls({expected_value}) returned {member.name!r}, expected {attr_name!r}."
        )

    @pytest.mark.parametrize("attr_name", list(_EXPECTED_MEMBERS))
    def test_lookup_by_name(self, attr_name):
        """``cls[name]`` must return the correct member (subscript access)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        member = cls[attr_name]
        assert member.name == attr_name, f"cls[{attr_name!r}] returned {member.name!r}."

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def test_iteration_yields_all_members(self):
        """``for m in cls`` must yield every expected member exactly once."""
        cls = _get_class("AutomaticNodeMovementMethod")
        names = {m.name for m in cls}
        assert names == set(_EXPECTED_MEMBERS), (
            f"Iteration yielded {names!r}, expected {set(_EXPECTED_MEMBERS)!r}."
        )

    def test_iteration_yields_enum_instances(self):
        """Every object yielded by iteration must be an Enum instance."""
        cls = _get_class("AutomaticNodeMovementMethod")
        for member in cls:
            assert isinstance(member, Enum), f"Iteration yielded non-Enum object: {member!r}."

    # ------------------------------------------------------------------
    # Comparison and identity
    # ------------------------------------------------------------------

    def test_same_member_equality(self):
        """A member must equal itself (``Off == Off``)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.Off == cls.Off

    def test_different_members_inequality(self):
        """Different members must not be equal (``Off != Aggressive``)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.Off != cls.Aggressive

    def test_member_identity(self):
        """Accessing the same member twice must return the identical object."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.Off is cls.Off

    def test_member_not_equal_to_raw_value(self):
        """An enum member must not compare equal to its raw integer value.

        Python Enum members are NOT equal to plain ints (unless IntEnum is
        used).  This verifies the class really is Enum-based, not int-based.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.Off != 0, (
            "AutomaticNodeMovementMethod.Off == 0 — the class may be IntEnum "
            "or the value is leaking as a plain int."
        )

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def test_members_are_hashable(self):
        """Enum members must be hashable (usable as dict keys / set members)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        member_set = set(cls)
        assert len(member_set) == len(_EXPECTED_MEMBERS), (
            "Not all members could be added to a set — hashing is broken."
        )

    def test_member_as_dict_key(self):
        """Enum members must work as dict keys."""
        cls = _get_class("AutomaticNodeMovementMethod")
        mapping = {m: m.value for m in cls}
        assert mapping[cls.Off] == 0

    def test_member_in_set(self):
        """``cls.Off in {cls.Off, cls.Aggressive}`` must be True."""
        cls = _get_class("AutomaticNodeMovementMethod")
        s = {cls.Off, cls.Aggressive}
        assert cls.Off in s
        assert cls.Conservative not in s

    # ------------------------------------------------------------------
    # String representations
    # ------------------------------------------------------------------

    def test_str_includes_member_name(self):
        """``str(member)`` must include the member name for hover documentation."""
        cls = _get_class("AutomaticNodeMovementMethod")
        s = str(cls.Off)
        assert "Off" in s, f"str(AutomaticNodeMovementMethod.Off) == {s!r} does not contain 'Off'."

    def test_repr_includes_class_and_member(self):
        """``repr(member)`` should include both the class and the member name."""
        cls = _get_class("AutomaticNodeMovementMethod")
        r = repr(cls.Off)
        assert "Off" in r, f"repr contains no member name: {r!r}."
        assert "AutomaticNodeMovementMethod" in r, f"repr contains no class name: {r!r}."

    # ------------------------------------------------------------------
    # Containment
    # ------------------------------------------------------------------

    def test_member_containment(self):
        """``cls.Off in cls`` must be True."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.Off in cls

    def test_non_member_not_contained(self):
        """A random integer must not be reported as contained in the enum."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert all(member.value != 999 for member in cls), (
            "Unexpected enum member with value 999 found in AutomaticNodeMovementMethod."
        )

    # ------------------------------------------------------------------
    # Docstring
    # ------------------------------------------------------------------

    def test_class_has_docstring(self):
        """The class must have a docstring (VS Code shows this in hover tips)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        assert cls.__doc__, (
            "AutomaticNodeMovementMethod has no docstring. "
            "VS Code hover documentation will be empty."
        )


# ===========================================================================
# TestAutomaticNodeMovementMethodNetMethods
# ===========================================================================


@_skip_no_version
@_skip_no_anmm
class TestAutomaticNodeMovementMethodNetMethods:
    """.NET System.Enum methods must be present on AutomaticNodeMovementMethod.

    Every .NET enum inherits from System.Enum, which provides GetHashCode,
    ToString, CompareTo, HasFlag, GetTypeCode, Equals, and GetType.  The stubs
    must expose these so VS Code autocomplete shows them when a user types
    ``my_method_value.<TAB>``.

    In v0.1.14 these methods only existed on the shadowing object-based class
    (which overwrote the Enum definition).  After the fix they live directly on
    the Enum-based class, so both the enum members AND the .NET methods are
    available.
    """

    _NET_METHODS = [
        "GetHashCode",
        "ToString",
        "CompareTo",
        "HasFlag",
        "GetTypeCode",
        "Equals",
        "GetType",
    ]

    @pytest.mark.parametrize("method_name", _NET_METHODS)
    def test_net_method_present(self, method_name):
        """Each .NET-inherited method must be accessible on the class.

        Pylance surfaces these in the member-completion list when the user
        types ``AutomaticNodeMovementMethod.Off.<TAB>``.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert hasattr(cls, method_name), (
            f"AutomaticNodeMovementMethod is missing the .NET method '{method_name}'. "
            "VS Code would not suggest it as a completion on enum instances."
        )

    @pytest.mark.parametrize("method_name", _NET_METHODS)
    def test_net_method_is_callable(self, method_name):
        """Each .NET-inherited method must be callable (not just an attribute)."""
        cls = _get_class("AutomaticNodeMovementMethod")
        method = getattr(cls, method_name)
        assert callable(method), f"AutomaticNodeMovementMethod.{method_name} is not callable."

    def test_class_is_still_enum_with_net_methods(self):
        """Having .NET methods must not prevent the class from being an Enum.

        The fix merges .NET methods INTO the Enum-based class, so both enum
        membership and .NET method access work simultaneously.
        """
        cls = _get_class("AutomaticNodeMovementMethod")
        assert issubclass(cls, Enum), (
            "AutomaticNodeMovementMethod lost its Enum base after .NET methods "
            "were added.  The class must inherit from both Enum and expose the "
            ".NET methods."
        )

    def test_enum_members_survive_net_methods(self):
        """Enum members must still be present alongside the .NET methods."""
        cls = _get_class("AutomaticNodeMovementMethod")
        for name in _EXPECTED_MEMBERS:
            assert hasattr(cls, name), f"Member '{name}' disappeared after .NET methods were added."


# ===========================================================================
# TestWorkingEnumControl  (reference enums that should always pass)
# ===========================================================================


@_skip_no_version
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

    _BASE_RESULT_SPOT = {"Mass": 5, "Displacement": 0, "Temperature": 1}

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


@_skip_no_version
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


@_skip_no_version
class TestEnumModuleExports:
    """Verify the Enums module exports all classes needed for VS Code autocomplete.

    The module-level ``dir()`` is what Pylance uses to build the completion
    list for ``from ansys...Enums import <TAB>``.  A class absent from
    ``dir(module)`` will not appear in that completion list.
    """

    _EXPECTED_EXPORTS = [
        "AutomaticNodeMovementMethod",
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
