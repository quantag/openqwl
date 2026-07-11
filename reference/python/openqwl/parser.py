"""
Parsing and structural validation for .openqwl documents.

Full validation against schema/openqwl.schema.json is preferred and is
attempted automatically if the `jsonschema` package is installed. If it
is not installed, we fall back to a small set of hand-written checks so
the reference runner still catches obviously malformed documents.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml


class OpenQWLValidationError(Exception):
    """Raised when a .openqwl document is structurally invalid."""


REQUIRED_TOP_LEVEL_KEYS = ("openqwl", "metadata", "workflow")
REQUIRED_NODE_KEYS = ("id", "uses")


@dataclass
class WorkflowDocument:
    """A parsed .openqwl document plus a resolved path, for error messages."""

    raw: dict[str, Any]
    path: str

    @property
    def version(self) -> str:
        return str(self.raw.get("openqwl", "unknown"))

    @property
    def metadata(self) -> dict[str, Any]:
        return self.raw.get("metadata", {})

    @property
    def nodes(self) -> list[dict[str, Any]]:
        return self.raw.get("workflow", {}).get("nodes", [])

    @property
    def edges(self) -> list[dict[str, Any]]:
        return self.raw.get("workflow", {}).get("edges", [])

    @property
    def exports(self) -> dict[str, Any]:
        return self.raw.get("exports", {})

    @property
    def metrics(self) -> list[str]:
        return self.raw.get("metrics", [])


def load_workflow(path: str) -> WorkflowDocument:
    """Load and validate a .openqwl file, returning a WorkflowDocument."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such .openqwl file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise OpenQWLValidationError(
            f"{path}: top-level document must be a YAML mapping"
        )

    _validate_structure(raw, path)
    _validate_with_schema_if_available(raw, path)

    return WorkflowDocument(raw=raw, path=path)


def _validate_structure(raw: dict[str, Any], path: str) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in raw]
    if missing:
        raise OpenQWLValidationError(
            f"{path}: missing required top-level key(s): {', '.join(missing)}"
        )

    nodes = raw.get("workflow", {}).get("nodes")
    if not nodes:
        raise OpenQWLValidationError(
            f"{path}: workflow.nodes must contain at least one node"
        )

    seen_ids = set()
    for i, node in enumerate(nodes):
        missing_node_keys = [k for k in REQUIRED_NODE_KEYS if k not in node]
        if missing_node_keys:
            raise OpenQWLValidationError(
                f"{path}: workflow.nodes[{i}] missing required key(s): "
                f"{', '.join(missing_node_keys)}"
            )
        if node["id"] in seen_ids:
            raise OpenQWLValidationError(
                f"{path}: duplicate node id '{node['id']}'"
            )
        seen_ids.add(node["id"])

    edges = raw.get("workflow", {}).get("edges", [])
    for i, edge in enumerate(edges):
        for key in ("from", "to"):
            if key not in edge:
                raise OpenQWLValidationError(
                    f"{path}: workflow.edges[{i}] missing required key '{key}'"
                )
            if edge[key] not in seen_ids:
                raise OpenQWLValidationError(
                    f"{path}: workflow.edges[{i}].{key} references unknown "
                    f"node id '{edge[key]}'"
                )


def _validate_with_schema_if_available(raw: dict[str, Any], path: str) -> None:
    try:
        import jsonschema
    except ImportError:
        return  # jsonschema not installed -- skip full schema validation

    schema_path = _find_schema_path()
    if schema_path is None:
        return  # schema not found relative to this file -- skip silently

    with open(schema_path, "r", encoding="utf-8") as f:
        import json

        schema = json.load(f)

    try:
        jsonschema.validate(instance=raw, schema=schema)
    except jsonschema.ValidationError as e:
        raise OpenQWLValidationError(f"{path}: schema validation failed: {e.message}")


def _find_schema_path() -> str | None:
    here = os.path.dirname(os.path.abspath(__file__))
    # reference/python/openqwl/ -> repo root is three levels up
    candidate = os.path.normpath(
        os.path.join(here, "..", "..", "..", "schema", "openqwl.schema.json")
    )
    return candidate if os.path.isfile(candidate) else None
