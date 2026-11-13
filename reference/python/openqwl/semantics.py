"""
Semantic checks introduced in OpenQWL Draft 0.2: composite nodes
(core/group, core/loop), kernels, execution tiers and targets.

The checks work on the raw YAML mapping, so both the reference runner
(parser.py) and the standalone validator (openqwl_validate.py) can use
them. `check_document` returns (errors, warnings); an empty error list
means the document passes every Draft 0.2 rule in SPEC.md section 26.
"""

from __future__ import annotations

from typing import Any

CORE_GROUP = "openqwl://core/group"
CORE_LOOP = "openqwl://core/loop"
CORE_KERNEL = "openqwl://core/kernel"
COMPOSITES = (CORE_GROUP, CORE_LOOP)

TIERS = ("queued", "session", "realtime", "auto")
KNOWN_CAPABILITIES = (
    "mid_circuit_measurement",
    "feed_forward",
    "qubit_reuse",
    "sessions",
)
UNTIL_OPERATORS = ("lt", "le", "gt", "ge", "eq")


def check_document(raw: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    execution = raw.get("execution") or {}
    targets = {t.get("id") for t in execution.get("targets") or [] if isinstance(t, dict)}
    default_tier = execution.get("tier", "auto")

    uses_02 = bool(execution.get("tier") or execution.get("targets"))
    nodes = (raw.get("workflow") or {}).get("nodes") or []
    edges = (raw.get("workflow") or {}).get("edges") or []

    state = _State(errors, warnings, targets)
    _check_graph(nodes, edges, "workflow", state, parent_tier=default_tier, parent_target=None)

    if (uses_02 or state.uses_02) and str(raw.get("openqwl")) == "0.1":
        errors.append(
            "document uses Draft 0.2 features (composite nodes, kernels, tiers or targets) "
            'and must declare openqwl: "0.2"'
        )

    return errors, warnings


class _State:
    def __init__(self, errors: list[str], warnings: list[str], targets: set[str]) -> None:
        self.errors = errors
        self.warnings = warnings
        self.targets = targets
        self.uses_02 = False


def _check_graph(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    where: str,
    state: _State,
    parent_tier: str,
    parent_target: str | None,
) -> None:
    ids: set[str] = set()
    for node in nodes:
        node_id = node.get("id")
        if node_id in ids:
            state.errors.append(f"{where}: duplicate node id '{node_id}'")
        ids.add(node_id)

    for i, edge in enumerate(edges):
        for key in ("from", "to"):
            if edge.get(key) not in ids:
                state.errors.append(
                    f"{where}.edges[{i}].{key}: unknown node id '{edge.get(key)}'"
                )

    if _has_cycle(ids, edges):
        state.errors.append(f"{where}: graph contains a cycle")

    for node in nodes:
        _check_node(node, f"{where}/{node.get('id')}", state, parent_tier, parent_target)


def _check_node(
    node: dict[str, Any],
    where: str,
    state: _State,
    parent_tier: str,
    parent_target: str | None,
) -> None:
    uses = node.get("uses", "")
    constraints = node.get("constraints") or {}
    tier = constraints.get("tier")
    target = constraints.get("target")
    kernel = node.get("kernel")
    body = node.get("body")

    if tier is not None or target is not None or "requires" in constraints:
        state.uses_02 = True
    if kernel is not None or body is not None or uses.startswith("openqwl://core/"):
        state.uses_02 = True

    if uses.startswith("openqwl://core/") and uses not in COMPOSITES + (CORE_KERNEL,):
        state.errors.append(f"{where}: unknown core component '{uses}'")

    # tier
    if tier is not None and tier not in TIERS:
        state.errors.append(f"{where}: tier must be one of {', '.join(TIERS)}")
    if tier == "realtime" and kernel is None:
        state.errors.append(f"{where}: tier 'realtime' requires a kernel on the same node")
    if parent_tier == "session" and tier == "queued":
        state.errors.append(f"{where}: tier 'queued' inside a 'session' composite node")

    # target
    if target is not None:
        if target not in state.targets:
            state.errors.append(f"{where}: target '{target}' is not declared in execution.targets")
        if parent_target is not None and target != parent_target:
            state.errors.append(
                f"{where}: target '{target}' differs from enclosing target '{parent_target}'"
            )

    # requires
    for name in constraints.get("requires") or []:
        if name not in KNOWN_CAPABILITIES:
            state.warnings.append(f"{where}: unknown capability '{name}' in constraints.requires")

    # kernel
    if kernel is not None:
        if not kernel.get("format"):
            state.errors.append(f"{where}: kernel.format is required")
        if ("source" in kernel) == ("inline" in kernel):
            state.errors.append(f"{where}: kernel needs exactly one of 'source' and 'inline'")
    if uses == CORE_KERNEL and kernel is None:
        state.errors.append(f"{where}: {CORE_KERNEL} requires a kernel")

    # composites
    if uses in COMPOSITES:
        if tier == "realtime":
            state.errors.append(
                f"{where}: a composite node cannot be 'realtime'; put real-time logic in a kernel"
            )
        if not isinstance(body, dict) or not body.get("nodes"):
            state.errors.append(f"{where}: {uses} requires a body with at least one node")
            return
        _check_composite(node, body, where, state)
        _check_graph(
            body.get("nodes") or [],
            body.get("edges") or [],
            where,
            state,
            parent_tier=tier or parent_tier,
            parent_target=target or parent_target,
        )
    elif body is not None:
        state.errors.append(f"{where}: 'body' is only allowed on {CORE_GROUP} or {CORE_LOOP}")


def _check_composite(node: dict[str, Any], body: dict[str, Any], where: str, state: _State) -> None:
    uses = node["uses"]
    inputs = node.get("inputs") or {}
    outputs = node.get("outputs") or {}
    params = node.get("parameters") or {}
    results = body.get("results") or {}
    carry = body.get("carry") or {}

    for port in results:
        if port not in outputs:
            state.errors.append(f"{where}: body.results key '{port}' is not a declared output")
    for port in outputs:
        if uses == CORE_LOOP and port not in results:
            state.errors.append(f"{where}: output '{port}' has no entry in body.results")

    if uses == CORE_GROUP:
        if carry:
            state.errors.append(f"{where}: body.carry is only allowed on {CORE_LOOP}")
        return

    max_iterations = params.get("max_iterations")
    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) or max_iterations < 1:
        state.errors.append(f"{where}: parameters.max_iterations must be a positive integer")

    for port in carry:
        if port not in inputs:
            state.errors.append(f"{where}: body.carry key '{port}' is not a declared input")

    until = params.get("until")
    if until is not None:
        if not isinstance(until, dict) or not until.get("variable"):
            state.errors.append(f"{where}: parameters.until needs a 'variable'")
        else:
            ops = [k for k in until if k in UNTIL_OPERATORS]
            if len(ops) != 1:
                state.errors.append(
                    f"{where}: parameters.until needs exactly one of {', '.join(UNTIL_OPERATORS)}"
                )


def _has_cycle(ids: set[str], edges: list[dict[str, Any]]) -> bool:
    graph: dict[str, list[str]] = {i: [] for i in ids}
    for edge in edges:
        if edge.get("from") in graph and edge.get("to") in graph:
            graph[edge["from"]].append(edge["to"])
    state: dict[str, int] = {}

    def visit(n: str) -> bool:
        if state.get(n) == 1:
            return True
        if state.get(n) == 2:
            return False
        state[n] = 1
        if any(visit(m) for m in graph[n]):
            return True
        state[n] = 2
        return False

    return any(visit(n) for n in ids)
