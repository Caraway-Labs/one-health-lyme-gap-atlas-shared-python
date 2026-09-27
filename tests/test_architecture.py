"""Enforce the approved portable import and dependency direction."""

import ast
import subprocess
import sys
import tomllib
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "lyme_gap_atlas_shared"
PORTABLE = (
    PACKAGE / "__init__.py",
    PACKAGE / "models.py",
    PACKAGE / "scoring.py",
    *(PACKAGE / "domain").rglob("*.py"),
)
FORBIDDEN = {
    "snowflake", "neo4j", "cryptography", "pydantic_settings",
    "opentelemetry", "fastapi", "mcp",
}


def test_portable_modules_do_not_import_runtime_dependencies() -> None:
    for path in PORTABLE:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
                assert not roots & FORBIDDEN, f"{path}: {roots & FORBIDDEN}"
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in FORBIDDEN, str(path)
                if node.level:
                    excluded = {
                        "infrastructure", "settings", "snowflake", "observability"
                    }
                    assert (node.module or "").split(".")[0] not in excluded, str(path)
                    assert not {alias.name for alias in node.names} & excluded, str(path)


def test_portable_import_does_not_load_runtime_modules() -> None:
    code = """import sys
import lyme_gap_atlas_shared.domain
assert not any(name.startswith(('snowflake', 'neo4j', 'cryptography',
    'pydantic_settings', 'opentelemetry', 'lyme_gap_atlas_shared.infrastructure'))
    for name in sys.modules)
"""
    subprocess.run([sys.executable, "-c", code], check=True)


def test_base_dependency_set_does_not_grant_persistence_or_telemetry() -> None:
    project = tomllib.loads((PACKAGE.parents[1] / "pyproject.toml").read_text())
    dependencies = project["project"]["dependencies"]
    assert dependencies == ["pydantic>=2.10,<3"]
    extras = project["project"]["optional-dependencies"]
    assert any("snowflake-connector-python" in item for item in extras["snowflake"])
    assert any("pydantic-settings" in item for item in extras["snowflake"])
    assert any("opentelemetry-sdk" in item for item in extras["observability"])
