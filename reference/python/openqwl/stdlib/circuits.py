"""
uses: openqwl://stdlib/circuits/*

Each function takes (parameters, inputs) and returns a dict of
{output_port_name: value}, matching the node's `outputs:` mapping.
"""

from __future__ import annotations

from typing import Any

from ..backends import Circuit


def bell(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/circuits/bell

    Builds an n-qubit GHZ/Bell-style entangled circuit:
    H on qubit 0, then CX(0, i) for every other qubit.
    parameters:
      qubits: int (default 2)
    """
    qubits = int(parameters.get("qubits", 2))
    if qubits < 1:
        raise ValueError("circuits/bell: 'qubits' must be >= 1")

    circuit = Circuit(qubits)
    circuit.h(0)
    for target in range(1, qubits):
        circuit.cx(0, target)

    return {"circuit": circuit}
