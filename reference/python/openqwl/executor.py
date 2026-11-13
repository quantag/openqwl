"""
Executes a parsed WorkflowDocument: topologically sorts workflow.nodes
using workflow.edges, runs each node's registered implementation in
order, and threads outputs to downstream inputs via a shared context
dict keyed by the *global* variable names declared in each node's
`outputs:` mapping.

Draft 0.2 composite nodes (openqwl://core/group, openqwl://core/loop)
run their body in a child scope: the body sees the enclosing variables
plus the composite node's input ports, writes only to its own scope,
and publishes `body.results` to the enclosing scope when it finishes.

The reference runner executes everything locally, so execution tiers
and targets are validated but have no effect on how nodes run here.
Kernels (openqwl://core/kernel) need a quantum runtime and are not
executed by this runner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .parser import WorkflowDocument
from .registry import resolve
from .semantics import CORE_GROUP, CORE_KERNEL, CORE_LOOP


class ExecutionError(Exception):
    pass


@dataclass
class ExecutionResult:
    context: dict[str, Any] = field(default_factory=dict)
    node_order: list[str] = field(default_factory=list)
    exported_files: list[str] = field(default_factory=list)
    iterations: dict[str, int] = field(default_factory=dict)


def topological_order(doc: WorkflowDocument) -> list[str]:
    """Kahn's algorithm over workflow.edges. Raises on cycles."""
    return _order(doc.nodes, doc.edges)


def _order(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
    node_ids = [n["id"] for n in nodes]
    in_degree = {nid: 0 for nid in node_ids}
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}

    for edge in edges:
        adjacency[edge["from"]].append(edge["to"])
        in_degree[edge["to"]] += 1

    ready = [nid for nid in node_ids if in_degree[nid] == 0]
    order: list[str] = []

    while ready:
        # Stable order: preserve declaration order among ready nodes.
        ready.sort(key=node_ids.index)
        current = ready.pop(0)
        order.append(current)
        for downstream in adjacency[current]:
            in_degree[downstream] -= 1
            if in_degree[downstream] == 0:
                ready.append(downstream)

    if len(order) != len(node_ids):
        remaining = set(node_ids) - set(order)
        raise ExecutionError(
            f"Cycle detected in workflow graph among node(s): {sorted(remaining)}"
        )

    return order


def run(doc: WorkflowDocument) -> ExecutionResult:
    order = topological_order(doc)
    result = ExecutionResult(node_order=order)
    _run_graph(doc.nodes, doc.edges, result.context, result, prefix="")
    return result


def _run_graph(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    scope: dict[str, Any],
    result: ExecutionResult,
    prefix: str,
) -> None:
    nodes_by_id = {n["id"]: n for n in nodes}
    for node_id in _order(nodes, edges):
        node = nodes_by_id[node_id]
        path = prefix + node_id
        resolved_inputs = _resolve_inputs(node, path, scope)

        if node["uses"] in (CORE_GROUP, CORE_LOOP):
            outputs = _run_composite(node, path, resolved_inputs, scope, result)
        elif node["uses"] == CORE_KERNEL:
            raise ExecutionError(
                f"Node '{path}' runs a {node['kernel'].get('format')} kernel. "
                f"The reference runner has no quantum runtime; use an "
                f"implementation that supports kernels."
            )
        else:
            fn = resolve(node["uses"])
            try:
                outputs = fn(node.get("parameters", {}), resolved_inputs)
            except Exception as e:  # noqa: BLE001 - surface node id in the error
                raise ExecutionError(f"Node '{path}' ({node['uses']}) failed: {e}") from e

        for local_port, global_var in node.get("outputs", {}).items():
            if local_port not in outputs:
                raise ExecutionError(
                    f"Node '{path}' declared output '{local_port}' but its "
                    f"implementation did not return it. Got: {list(outputs)}"
                )
            scope[global_var] = outputs[local_port]
            if local_port == "file":
                result.exported_files.append(outputs[local_port])


def _resolve_inputs(node: dict[str, Any], path: str, scope: dict[str, Any]) -> dict[str, Any]:
    resolved = {}
    for local_port, global_var in node.get("inputs", {}).items():
        if global_var not in scope:
            raise ExecutionError(
                f"Node '{path}' requires input '{local_port}' "
                f"('{global_var}'), which has not been produced yet. "
                f"Check workflow.edges for a missing dependency."
            )
        resolved[local_port] = scope[global_var]
    return resolved


_COMPARE = {
    "lt": lambda a, b: a < b,
    "le": lambda a, b: a <= b,
    "gt": lambda a, b: a > b,
    "ge": lambda a, b: a >= b,
    "eq": lambda a, b: a == b,
}


def _run_composite(
    node: dict[str, Any],
    path: str,
    inputs: dict[str, Any],
    outer: dict[str, Any],
    result: ExecutionResult,
) -> dict[str, Any]:
    body = node["body"]
    params = node.get("parameters", {})
    is_loop = node["uses"] == CORE_LOOP
    max_iterations = params.get("max_iterations", 1) if is_loop else 1
    until = params.get("until") if is_loop else None
    carry = body.get("carry", {})

    loop_vars = dict(inputs)
    inner: dict[str, Any] = {}
    iterations = 0
    while iterations < max_iterations:
        inner = {**outer, **loop_vars}
        _run_graph(body["nodes"], body.get("edges", []), inner, result, prefix=path + "/")
        iterations += 1

        if until is not None and _until_holds(until, inner, path):
            break
        for port, body_var in carry.items():
            if body_var not in inner:
                raise ExecutionError(f"Node '{path}': carry variable '{body_var}' was not produced")
            loop_vars[port] = inner[body_var]

    result.iterations[path] = iterations

    outputs = {}
    for port, body_var in body.get("results", {}).items():
        if body_var not in inner:
            raise ExecutionError(f"Node '{path}': result variable '{body_var}' was not produced")
        outputs[port] = inner[body_var]
    return outputs


def _until_holds(until: dict[str, Any], scope: dict[str, Any], path: str) -> bool:
    variable = until["variable"]
    if variable not in scope:
        raise ExecutionError(f"Node '{path}': until variable '{variable}' was not produced")
    op = next(k for k in until if k in _COMPARE)
    return _COMPARE[op](scope[variable], until[op])


def collect_metrics(doc: WorkflowDocument, result: ExecutionResult) -> dict[str, Any]:
    """
    Computes the metrics listed in the document's top-level `metrics:`
    block. Reports them for every circuit-like object found in the
    execution context (anything exposing gate_count/depth/num_qubits) --
    for a single-circuit workflow like bell.openqwl there is exactly one.
    """
    circuits = {
        name: value
        for name, value in result.context.items()
        if hasattr(value, "gate_count") and hasattr(value, "depth")
    }

    report: dict[str, Any] = {}
    for name, circuit in circuits.items():
        values: dict[str, Any] = {}
        for metric in doc.metrics:
            if metric == "qubit_count":
                values[metric] = circuit.num_qubits
            elif metric == "gate_count":
                values[metric] = circuit.gate_count()
            elif metric == "circuit_depth":
                values[metric] = circuit.depth()
            else:
                values[metric] = "unsupported by reference implementation"
        report[name] = values

    return report
