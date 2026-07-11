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

from .stdlib import circuits, export

NodeFn = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

REGISTRY: dict[str, NodeFn] = {
    "openqwl://stdlib/circuits/bell": circuits.bell,
    "openqwl://stdlib/export/qasm": export.qasm,
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
