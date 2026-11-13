"""
uses: openqwl://stdlib/chemistry/*
"""

from __future__ import annotations

from typing import Any
from ..backends import Circuit

def electronic_structure(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/chemistry/electronic_structure"""
    return {"hamiltonian": {"type": "molecular_hamiltonian"}}

def uccsd(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/chemistry/uccsd"""
    return {"ansatz": {"type": "uccsd_ansatz"}, "initial_params": [0.0]}


# Mock energy landscape for H2 with a single UCCSD parameter: a parabola
# with its minimum at the known ground-state energy. It lets the
# session-loop example run end to end without a quantum backend.
_H2_GROUND_STATE = -1.137
_H2_OPTIMAL_THETA = 0.113
_H2_CURVATURE = 0.5


def estimate_energy(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/chemistry/estimate_energy

    One energy estimate for the given ansatz parameters, plus its
    gradient. A real implementation runs the ansatz circuit on a
    backend (one job per call; inside a session these calls share one
    reservation of the device).
    """
    theta = inputs["params"][0]
    offset = theta - _H2_OPTIMAL_THETA
    return {
        "energy": _H2_GROUND_STATE + _H2_CURVATURE * offset ** 2,
        "gradient": [2 * _H2_CURVATURE * offset],
    }

def vqe(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/chemistry/vqe"""
    optimizer = parameters.get("optimizer", "COBYLA")
    maxiter = parameters.get("maxiter", 100)
    
    # Mock VQE circuit output
    circuit = Circuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    
    return {"circuit": circuit, "energy": -1.137}
