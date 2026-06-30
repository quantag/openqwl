#!/usr/bin/env python3
"""
OpenQWL Draft 0.1 validator.

Validates:
- YAML syntax
- JSON Schema
- unique node IDs
- edge references
- declared input/output references
- DAG cycles
- openqwl:// URI usage in node.uses
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml
from jsonschema import Draft202012Validator


class ValidationError(Exception):
    pass


def load_yaml(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValidationError(f"YAML parse error in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError(f"{path}: root document must be a YAML object")

    return data


def load_schema(schema_path: Path) -> Dict[str, Any]:
    try:
        with schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise ValidationError(f"Cannot load schema {schema_path}: {exc}") from exc


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any], path: Path) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    if errors:
        messages = []
        for err in errors:
            loc = ".".join(str(p) for p in err.path) or "<root>"
            messages.append(f"{path}: schema error at {loc}: {err.message}")
        raise ValidationError("\n".join(messages))


def get_nodes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    workflow = data.get("workflow", {})
    nodes = workflow.get("nodes", [])
    if not isinstance(nodes, list):
        raise ValidationError("workflow.nodes must be a list")
    return nodes


def get_edges(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    workflow = data.get("workflow", {})
    edges = workflow.get("edges", [])
    if edges is None:
        return []
    if not isinstance(edges, list):
        raise ValidationError("workflow.edges must be a list")
    return edges


def validate_node_ids(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}

    for node in nodes:
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            raise ValidationError("Each node must have a non-empty string id")

        if node_id in seen:
            raise ValidationError(f"Duplicate node id: {node_id}")

        seen[node_id] = node

    return seen


def validate_uses_uris(nodes: List[Dict[str, Any]]) -> None:
    for node in nodes:
        node_id = node.get("id")
        uses = node.get("uses")

        if not isinstance(uses, str) or not uses:
            raise ValidationError(f"Node {node_id}: uses must be a non-empty string")

        if not uses.startswith("openqwl://"):
            raise ValidationError(
                f"Node {node_id}: uses must start with openqwl://, got: {uses}"
            )


def validate_edges(
    edges: List[Dict[str, Any]],
    node_map: Dict[str, Dict[str, Any]],
) -> None:
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        output = edge.get("output")
        input_name = edge.get("input")

        if source not in node_map:
            raise ValidationError(f"Edge references unknown source node: {source}")

        if target not in node_map:
            raise ValidationError(f"Edge references unknown target node: {target}")

        if output is not None:
            source_outputs = node_map[source].get("outputs", {})
            if not isinstance(source_outputs, dict):
                raise ValidationError(f"Node {source}: outputs must be an object")
            if output not in source_outputs:
                raise ValidationError(
                    f"Edge {source}->{target}: output '{output}' not declared by node {source}"
                )

        if input_name is not None:
            target_inputs = node_map[target].get("inputs", {})
            if not isinstance(target_inputs, dict):
                raise ValidationError(f"Node {target}: inputs must be an object")
            if input_name not in target_inputs:
                raise ValidationError(
                    f"Edge {source}->{target}: input '{input_name}' not declared by node {target}"
                )


def validate_dag(edges: List[Dict[str, Any]], node_ids: Set[str]) -> None:
    graph: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}

    for edge in edges:
        source = edge["from"]
        target = edge["to"]
        graph[source].append(target)

    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValidationError(f"Workflow graph contains a cycle involving node: {node}")

        if node in visited:
            return

        visiting.add(node)

        for next_node in graph.get(node, []):
            visit(next_node)

        visiting.remove(node)
        visited.add(node)

    for node_id in node_ids:
        visit(node_id)


def validate_openqwl(path: Path, schema_path: Path) -> None:
    data = load_yaml(path)
    schema = load_schema(schema_path)

    validate_schema(data, schema, path)

    nodes = get_nodes(data)
    edges = get_edges(data)

    node_map = validate_node_ids(nodes)

    validate_uses_uris(nodes)
    validate_edges(edges, node_map)
    validate_dag(edges, set(node_map.keys()))


def find_default_schema() -> Path:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]
    return repo_root / "schema" / "openqwl.schema.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate OpenQWL Draft 0.1 documents.")
    parser.add_argument("files", nargs="+", help="OpenQWL files to validate")
    parser.add_argument(
        "--schema",
        default=str(find_default_schema()),
        help="Path to openqwl.schema.json",
    )

    args = parser.parse_args()

    schema_path = Path(args.schema)

    ok = True

    for file_name in args.files:
        path = Path(file_name)

        try:
            validate_openqwl(path, schema_path)
            print(f"VALID: {path}")
        except ValidationError as exc:
            ok = False
            print(f"INVALID: {path}", file=sys.stderr)
            print(str(exc), file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())