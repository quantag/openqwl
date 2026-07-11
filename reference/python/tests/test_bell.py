import os
import unittest

from openqwl.executor import collect_metrics, run
from openqwl.parser import load_workflow

EXAMPLES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "examples")
)


class TestBellExample(unittest.TestCase):
    def test_runs_end_to_end(self):
        doc = load_workflow(os.path.join(EXAMPLES_DIR, "bell.openqwl"))
        result = run(doc)

        self.assertEqual(result.node_order, ["create_bell", "export_qasm"])
        self.assertIn("output/bell.qasm", result.exported_files)
        self.assertTrue(os.path.isfile("output/bell.qasm"))

        metrics = collect_metrics(doc, result)
        self.assertEqual(metrics["bell_circuit"]["qubit_count"], 2)
        self.assertEqual(metrics["bell_circuit"]["gate_count"], 2)
        self.assertEqual(metrics["bell_circuit"]["circuit_depth"], 2)

    def test_qasm_output_is_valid_looking(self):
        doc = load_workflow(os.path.join(EXAMPLES_DIR, "bell.openqwl"))
        run(doc)

        with open("output/bell.qasm", "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("OPENQASM 3.0;", content)
        self.assertIn("h q[0];", content)
        self.assertIn("cx q[0], q[1];", content)


if __name__ == "__main__":
    unittest.main()
