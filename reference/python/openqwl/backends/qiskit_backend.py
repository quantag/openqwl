"""
Qiskit-backed circuit backend.

Only imported if `qiskit` is installed. Wraps qiskit.QuantumCircuit
behind the same minimal interface as backends.simple.SimpleCircuit
(h, cx, gate_count, depth, to_qasm3) so the stdlib nodes and executor
don't need to know which backend is active.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


class QiskitCircuit:
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self._qc = QuantumCircuit(num_qubits)

    def h(self, qubit: int) -> "QiskitCircuit":
        self._qc.h(qubit)
        return self

    def cx(self, control: int, target: int) -> "QiskitCircuit":
        self._qc.cx(control, target)
        return self

    def gate_count(self) -> int:
        return sum(self._qc.count_ops().values())

    def depth(self) -> int:
        return self._qc.depth()

    def to_qasm3(self) -> str:
        from qiskit.qasm3 import dumps

        return dumps(self._qc)


def backend_name() -> str:
    import qiskit

    return f"qiskit {qiskit.__version__}"
