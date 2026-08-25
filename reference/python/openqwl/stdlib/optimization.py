"""
uses: openqwl://stdlib/optimization/*
"""

from __future__ import annotations

from typing import Any
from ..backends import Circuit

def maxcut_to_qubo(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/optimization/maxcut/to_qubo"""
    # mock conversion
    return {"qubo": {"type": "QUBO", "problem": "maxcut"}}

def tsp_to_qubo(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/optimization/tsp/to_qubo"""
    # mock conversion
    return {"qubo": {"type": "QUBO", "problem": "tsp"}}

def qubo_to_ising(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/optimization/qubo/to_ising"""
    qubo = inputs.get("qubo", {})
    return {"hamiltonian": {"type": "Ising", "from_qubo": qubo}}

def qaoa(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/optimization/qaoa"""
    p = parameters.get("p", 1)
    # mock circuit
    circuit = Circuit(2)
    circuit.h(0)
    circuit.h(1)
    for _ in range(int(p)):
        circuit.cx(0, 1)
    return {"circuit": circuit}

def tsp_decode(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/optimization/tsp/decode"""
    return {"solution": {"route": [0, 1, 2, 0]}}
