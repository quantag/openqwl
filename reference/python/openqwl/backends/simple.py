"""
A minimal, dependency-free circuit backend.

This exists so the reference runner works immediately with nothing but
PyYAML installed. It supports exactly the gates the bundled stdlib nodes
need (h, cx). It is intentionally not a simulator or a serious circuit
library -- swap in the Qiskit backend (backends/qiskit_backend.py) for
anything real.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimpleCircuit:
    num_qubits: int
    gates: list[tuple[str, tuple[int, ...]]] = field(default_factory=list)

    def h(self, qubit: int) -> "SimpleCircuit":
        self.gates.append(("h", (qubit,)))
        return self

    def cx(self, control: int, target: int) -> "SimpleCircuit":
        self.gates.append(("cx", (control, target)))
        return self

    # --- metrics -----------------------------------------------------

    def gate_count(self) -> int:
        return len(self.gates)

    def depth(self) -> int:
        """Longest chain of gates touching a shared qubit (layered schedule)."""
        qubit_layer = [0] * self.num_qubits
        for _, qubits in self.gates:
            layer = max(qubit_layer[q] for q in qubits) + 1
            for q in qubits:
                qubit_layer[q] = layer
        return max(qubit_layer, default=0)

    # --- export --------------------------------------------------------

    def to_qasm3(self) -> str:
        lines = [
            "OPENQASM 3.0;",
            'include "stdgates.inc";',
            f"qubit[{self.num_qubits}] q;",
        ]
        for name, qubits in self.gates:
            if name == "h":
                lines.append(f"h q[{qubits[0]}];")
            elif name == "cx":
                lines.append(f"cx q[{qubits[0]}], q[{qubits[1]}];")
            else:
                raise NotImplementedError(f"gate '{name}' not supported by SimpleCircuit")
        return "\n".join(lines) + "\n"


def backend_name() -> str:
    return "simple (built-in, no external dependencies)"
