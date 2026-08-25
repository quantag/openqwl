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

def ghz(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/circuits/ghz

    Builds an n-qubit GHZ state circuit.
    parameters:
      qubits: int (default 3)
    """
    qubits = int(parameters.get("qubits", 3))
    if qubits < 1:
        raise ValueError("circuits/ghz: 'qubits' must be >= 1")

    circuit = Circuit(qubits)
    circuit.h(0)
    for target in range(1, qubits):
        circuit.cx(0, target)

    return {"circuit": circuit}

def teleportation(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/circuits/teleportation
    
    Builds a 3-qubit quantum teleportation circuit.
    """
    circuit = Circuit(3)
    # create entangled pair between q1 and q2
    circuit.h(1)
    circuit.cx(1, 2)
    
    # Alice performs Bell measurement on q0 (message) and q1
    circuit.cx(0, 1)
    circuit.h(0)
    
    # Bob applies conditional corrections (mocked as simple CX/H for this example since we don't have classical if yet)
    circuit.cx(1, 2)
    circuit.h(2)
    circuit.cx(0, 2)
    circuit.h(2)
    
    return {"circuit": circuit}

def qft(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/circuits/qft
    
    Builds a Quantum Fourier Transform circuit.
    parameters:
      qubits: int (default 3)
    """
    qubits = int(parameters.get("qubits", 3))
    circuit = Circuit(qubits)
    
    # simplified mock QFT circuit (just to show the node execution)
    for i in range(qubits):
        circuit.h(i)
        for j in range(i + 1, qubits):
            circuit.cx(i, j) # mock controlled phase
            
    return {"circuit": circuit}
