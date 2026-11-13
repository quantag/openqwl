"""Draft 0.2: composite nodes, kernels, execution tiers and targets."""

import os
import tempfile
import textwrap
import unittest

import yaml

from openqwl import registry
from openqwl.executor import ExecutionError, run
from openqwl.parser import OpenQWLValidationError, load_workflow

EXAMPLES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "examples")
)


def _halve(parameters, inputs):
    """Toy optimiser step: halves x and reports how much it moved."""
    x = inputs["x"]
    return {"x": x / 2, "delta": x / 2}


def _add(parameters, inputs):
    return {"sum": inputs["a"] + parameters.get("b", 0)}


def _load(text):
    fd, path = tempfile.mkstemp(suffix=".openqwl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(text))
    try:
        return load_workflow(path)
    finally:
        os.remove(path)


def _loop_doc(**overrides):
    doc = {
        "openqwl": "0.2",
        "metadata": {"name": "loop", "version": "1.0"},
        "workflow": {
            "nodes": [
                {"id": "seed", "uses": "openqwl://test/add",
                 "inputs": {"a": "start"}, "outputs": {"sum": "x0"}, "parameters": {"b": 0}},
                {
                    "id": "shrink",
                    "uses": "openqwl://core/loop",
                    "inputs": {"x": "x0"},
                    "outputs": {"x": "x_final"},
                    "parameters": {"max_iterations": 50, "until": {"variable": "delta", "lt": 0.01}},
                    "body": {
                        "nodes": [
                            {"id": "step", "uses": "openqwl://test/halve",
                             "inputs": {"x": "x"}, "outputs": {"x": "x_next", "delta": "delta"}},
                        ],
                        "carry": {"x": "x_next"},
                        "results": {"x": "x_next"},
                    },
                },
            ],
            "edges": [{"from": "seed", "to": "shrink", "output": "sum", "input": "x"}],
        },
    }
    loop = doc["workflow"]["nodes"][1]
    for key, value in overrides.items():
        if key == "openqwl":
            doc["openqwl"] = value
        else:
            loop[key] = value
    return doc


class TierTestBase(unittest.TestCase):
    def setUp(self):
        registry.REGISTRY["openqwl://test/halve"] = _halve
        registry.REGISTRY["openqwl://test/add"] = _add

    def tearDown(self):
        registry.REGISTRY.pop("openqwl://test/halve", None)
        registry.REGISTRY.pop("openqwl://test/add", None)


class TestLoopExecution(TierTestBase):
    def test_loop_stops_on_until(self):
        doc = _load(yaml.safe_dump(_loop_doc()))
        result = _run_with_start(doc, 1.0)
        # 1 -> 0.5 (delta 0.5), ... stops when delta < 0.01: 1/2^7 = 0.0078
        self.assertEqual(result.iterations["shrink"], 7)
        self.assertAlmostEqual(result.context["x_final"], 1 / 2**7)

    def test_loop_stops_at_max_iterations(self):
        doc = _loop_doc()
        doc["workflow"]["nodes"][1]["parameters"] = {"max_iterations": 3}
        result = _run_with_start(_load(yaml.safe_dump(doc)), 1.0)
        self.assertEqual(result.iterations["shrink"], 3)
        self.assertAlmostEqual(result.context["x_final"], 0.125)

    def test_body_variables_do_not_leak(self):
        result = _run_with_start(_load(yaml.safe_dump(_loop_doc())), 1.0)
        self.assertNotIn("x_next", result.context)
        self.assertNotIn("delta", result.context)

    def test_group_runs_once(self):
        doc = _loop_doc()
        group = doc["workflow"]["nodes"][1]
        group["uses"] = "openqwl://core/group"
        group["parameters"] = {}
        del group["body"]["carry"]
        result = _run_with_start(_load(yaml.safe_dump(doc)), 1.0)
        self.assertEqual(result.iterations["shrink"], 1)
        self.assertAlmostEqual(result.context["x_final"], 0.5)


def _run_with_start(doc, start):
    # Seed the outer scope the way an import would.
    from openqwl.executor import ExecutionResult, _run_graph, topological_order

    result = ExecutionResult(node_order=topological_order(doc))
    result.context["start"] = start
    _run_graph(doc.nodes, doc.edges, result.context, result, prefix="")
    return result


class TestValidation(TierTestBase):
    def assertInvalid(self, doc, fragment):
        with self.assertRaises(OpenQWLValidationError) as ctx:
            _load(yaml.safe_dump(doc))
        self.assertIn(fragment, str(ctx.exception))

    def test_draft_01_cannot_use_loops(self):
        self.assertInvalid(_loop_doc(openqwl="0.1"), 'must declare openqwl: "0.2"')

    def test_max_iterations_required(self):
        self.assertInvalid(_loop_doc(parameters={}), "max_iterations")

    def test_carry_key_must_be_input(self):
        doc = _loop_doc()
        doc["workflow"]["nodes"][1]["body"]["carry"] = {"y": "x_next"}
        self.assertInvalid(doc, "body.carry key 'y'")

    def test_realtime_needs_kernel(self):
        doc = _loop_doc()
        doc["workflow"]["nodes"][1]["body"]["nodes"][0]["constraints"] = {"tier": "realtime"}
        self.assertInvalid(doc, "requires a kernel")

    def test_composite_cannot_be_realtime(self):
        self.assertInvalid(_loop_doc(constraints={"tier": "realtime"}), "composite node cannot be 'realtime'")

    def test_queued_inside_session(self):
        doc = _loop_doc(constraints={"tier": "session"})
        doc["workflow"]["nodes"][1]["body"]["nodes"][0]["constraints"] = {"tier": "queued"}
        self.assertInvalid(doc, "inside a 'session'")

    def test_undeclared_target(self):
        self.assertInvalid(_loop_doc(constraints={"target": "qpu"}), "not declared in execution.targets")

    def test_kernel_needs_one_source(self):
        doc = _loop_doc()
        doc["workflow"]["nodes"].append({
            "id": "k", "uses": "openqwl://core/kernel",
            "kernel": {"format": "openqasm3", "source": "a.qasm", "inline": "OPENQASM 3.0;"},
        })
        with self.assertRaises(OpenQWLValidationError):
            _load(yaml.safe_dump(doc))

    def test_unknown_capability_is_a_warning(self):
        doc = _loop_doc(constraints={"tier": "session", "requires": ["sessions", "teleporter"]})
        loaded = _load(yaml.safe_dump(doc))
        self.assertTrue(any("teleporter" in w for w in loaded.warnings))


class TestExamples(TierTestBase):
    def test_new_examples_validate(self):
        for name in ("vqe-h2-session.openqwl", "teleportation-realtime.openqwl"):
            with self.subTest(name=name):
                load_workflow(os.path.join(EXAMPLES_DIR, name))

    def test_draft_01_examples_still_validate(self):
        load_workflow(os.path.join(EXAMPLES_DIR, "bell.openqwl"))

    def test_kernel_nodes_need_a_quantum_runtime(self):
        doc = load_workflow(os.path.join(EXAMPLES_DIR, "teleportation-realtime.openqwl"))
        with self.assertRaises(ExecutionError) as ctx:
            run(doc)
        self.assertIn("no quantum runtime", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
