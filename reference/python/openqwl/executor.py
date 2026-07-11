"""
Executes a parsed WorkflowDocument: topologically sorts workflow.nodes
using workflow.edges, runs each node's registered implementation in
order, and threads outputs to downstream inputs via a shared context
dict keyed by the *global* variable names declared in each node's
`outputs:` mapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .parser import WorkflowDocument
from .registry import resolve


class ExecutionError(Exception):
    pass


@dataclass
class ExecutionResult:
    context: dict[str, Any] = field(default_factory=dict)
    node_order: list[str] = field(default_factory=list)
    exported_files: list[str] = field(default_factory=list)


def topological_order(doc: WorkflowDocument) -> list[str]:
    """Kahn's algorithm over workflow.edges. Raises on cycles."""
    node_ids = [n["id"] for n in doc.nodes]
    in_degree = {nid: 0 for nid in node_ids}
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}

    for edge in doc.edges:
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
    nodes_by_id = {n["id"]: n for n in doc.nodes}
    order = topological_order(doc)

    result = ExecutionResult(node_order=order)

    for node_id in order:
        node = nodes_by_id[node_id]
        fn = resolve(node["uses"])

        parameters = node.get("parameters", {})
        input_ports = node.get("inputs", {})
        output_ports = node.get("outputs", {})

        resolved_inputs = {}
        for local_port, global_var in input_ports.items():
            if global_var not in result.context:
                raise ExecutionError(
                    f"Node '{node_id}' requires input '{local_port}' "
                    f"('{global_var}'), which has not been produced yet. "
                    f"Check workflow.edges for a missing dependency."
                )
            resolved_inputs[local_port] = result.context[global_var]

        try:
            outputs = fn(parameters, resolved_inputs)
        except Exception as e:  # noqa: BLE001 - surface node id in the error
            raise ExecutionError(f"Node '{node_id}' ({node['uses']}) failed: {e}") from e

        for local_port, global_var in output_ports.items():
            if local_port not in outputs:
                raise ExecutionError(
                    f"Node '{node_id}' declared output '{local_port}' but its "
                    f"implementation did not return it. Got: {list(outputs)}"
                )
            result.context[global_var] = outputs[local_port]
            if local_port == "file":
                result.exported_files.append(outputs[local_port])

    return result


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
