"""
Backend selection.

Any object with (num_qubits, h, cx, gate_count, depth, to_qasm3) satisfies
the "circuit backend" protocol the stdlib nodes expect. This module picks
the best one available at import time so the rest of the code never has
to branch on what's installed.
"""

from __future__ import annotations

try:
    from . import qiskit_backend as _active

    Circuit = _active.QiskitCircuit
    backend_name = _active.backend_name
except ImportError:
    from . import simple as _active

    Circuit = _active.SimpleCircuit
    backend_name = _active.backend_name
