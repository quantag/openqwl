"""
uses: openqwl://stdlib/search/*
"""

from __future__ import annotations

from typing import Any

from ..backends import Circuit


def oracle(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/search/oracle"""
    target = parameters.get("target", "101")
    return {"oracle": {"type": "oracle", "target": target}}


def diffuser(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/search/diffuser"""
    qubits = parameters.get("qubits", 3)
    return {"diffuser": {"type": "diffuser", "qubits": int(qubits)}}


def grover(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/search/grover"""
    oracle_obj = inputs.get("oracle", {})
    diffuser_obj = inputs.get("diffuser", {})
    
    qubits = diffuser_obj.get("qubits", 3)
    if not isinstance(qubits, int):
        qubits = 3
        
    circuit = Circuit(qubits)
    
    # 1. Initialize superposition
    for i in range(qubits):
        circuit.h(i)
        
    # 2. Mock iterations for the sake of the workflow example
    # Since SimpleCircuit only supports h and cx, we mock the oracle/diffuser
    circuit.cx(0, 1)
    if qubits > 2:
        circuit.cx(1, 2)
    circuit.h(0)
        
    return {"circuit": circuit}
