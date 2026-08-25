"""
Maps `uses:` URIs to Python callables.

This is deliberately a plain dict, not a plugin/entry-point system --
the goal of this reference implementation is to make adding a new
stdlib node a one-line, obvious change. A real implementation would
likely resolve `openqwl://` URIs against a package registry (see
REGISTRY.md in the repo root); this is the local, hardcoded version of
that for the handful of nodes needed to run the bundled examples.
"""

from __future__ import annotations

from typing import Any, Callable

from .stdlib import circuits, export, search, optimization, chemistry, runtime

NodeFn = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

REGISTRY: dict[str, NodeFn] = {
    "openqwl://stdlib/circuits/bell": circuits.bell,
    "openqwl://stdlib/circuits/ghz": circuits.ghz,
    "openqwl://stdlib/circuits/teleportation": circuits.teleportation,
    "openqwl://stdlib/circuits/qft": circuits.qft,
    "openqwl://stdlib/export/qasm": export.qasm,
    "openqwl://stdlib/search/oracle": search.oracle,
    "openqwl://stdlib/search/diffuser": search.diffuser,
    "openqwl://stdlib/search/grover": search.grover,
    "openqwl://stdlib/optimization/maxcut/to_qubo": optimization.maxcut_to_qubo,
    "openqwl://stdlib/optimization/tsp/to_qubo": optimization.tsp_to_qubo,
    "openqwl://stdlib/optimization/qubo/to_ising": optimization.qubo_to_ising,
    "openqwl://stdlib/optimization/qaoa": optimization.qaoa,
    "openqwl://stdlib/optimization/tsp/decode": optimization.tsp_decode,
    "openqwl://stdlib/chemistry/electronic_structure": chemistry.electronic_structure,
    "openqwl://stdlib/chemistry/uccsd": chemistry.uccsd,
    "openqwl://stdlib/chemistry/vqe": chemistry.vqe,
    "openqwl://runtime/qiskit": runtime.qiskit,
}


class UnknownNodeError(Exception):
    pass


def resolve(uses: str) -> NodeFn:
    try:
        return REGISTRY[uses]
    except KeyError:
        available = ", ".join(sorted(REGISTRY)) or "(none registered)"
        raise UnknownNodeError(
            f"No stdlib implementation registered for '{uses}'.\n"
            f"Available: {available}"
        )
