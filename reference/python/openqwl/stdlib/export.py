"""
uses: openqwl://stdlib/export/*
"""

from __future__ import annotations

import os
from typing import Any


def qasm(parameters: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """openqwl://stdlib/export/qasm

    parameters:
      format: "openqasm3"  (only format currently supported)
      path:   output file path, created relative to the current working
              directory if not absolute
    inputs:
      circuit: a backend circuit object (must implement to_qasm3())
    """
    fmt = parameters.get("format", "openqasm3")
    if fmt != "openqasm3":
        raise NotImplementedError(f"export/qasm: unsupported format '{fmt}'")

    path = parameters["path"]
    circuit = inputs["circuit"]

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(circuit.to_qasm3())

    return {"file": path}
