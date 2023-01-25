"""Test the imports to dependencies comparison function."""
from pathlib import Path
from typing import List

import pytest

from fawltydeps.check import compare_imports_to_dependencies
from fawltydeps.types import (
    DeclaredDependency,
    Location,
    ParsedImport,
    UndeclaredDependency,
    UnusedDependency,
)


def imports_factory(*imports: str) -> List[ParsedImport]:
    return [ParsedImport(imp, Location("<stdin>")) for imp in imports]


def deps_factory(*deps: str) -> List[DeclaredDependency]:
    return [DeclaredDependency(dep, Location(Path("foo"))) for dep in deps]


def undeclared_factory(*deps: str) -> List[UndeclaredDependency]:
    return [UndeclaredDependency(dep, imports_factory(dep)) for dep in deps]


def unused_factory(*deps: str) -> List[UnusedDependency]:
    return [UnusedDependency(dep, deps_factory(dep)) for dep in deps]


@pytest.mark.parametrize(
    "imports,dependencies,expected",
    [
        pytest.param([], [], ([], []), id="no_import_no_dependencies"),
        pytest.param(
            imports_factory("pandas"),
            [],
            (undeclared_factory("pandas"), []),
            id="one_import_no_dependencies",
        ),
        pytest.param(
            [],
            deps_factory("pandas"),
            ([], unused_factory("pandas")),
            id="no_imports_one_dependency",
        ),
        pytest.param(
            imports_factory("pandas"),
            deps_factory("pandas"),
            ([], []),
            id="matched_import_with_dependency",
        ),
        pytest.param(
            imports_factory("pandas", "numpy"),
            deps_factory("pandas", "scipy"),
            (undeclared_factory("numpy"), unused_factory("scipy")),
            id="mixed_imports_with_unused_and_undeclared_dependencies",
        ),
        pytest.param(
            imports_factory("pandas")
            + [ParsedImport("numpy", Location(Path("my_file.py"), lineno=3))],
            deps_factory("pandas", "scipy"),
            (
                [
                    UndeclaredDependency(
                        "numpy",
                        [ParsedImport("numpy", Location(Path("my_file.py"), lineno=3))],
                    )
                ],
                unused_factory("scipy"),
            ),
            id="mixed_imports_from_diff_files_with_unused_and_undeclared_dependencies",
        ),
    ],
)
def test_compare_imports_to_dependencies(imports, dependencies, expected):
    """Ensures the comparison method returns the expected unused and undeclared dependencies"""
    obtained = compare_imports_to_dependencies(imports, dependencies)
    assert obtained == expected
