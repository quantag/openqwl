"""
OpenQWL reference implementation.

A small, dependency-light interpreter for the OpenQWL workflow format.
This is NOT the final engine for the language -- it is a minimal,
readable reference that proves the document model (problem / workflow
DAG / exports / metrics) is executable, and gives implementers a
starting point to build real backends against.

Design goals for this reference implementation, in priority order:
  1. Runs with zero third-party dependencies (uses a built-in fallback
     circuit backend) so anyone can try it immediately.
  2. Upgrades transparently to Qiskit if it is installed, to produce
     real OpenQASM 3 output.
  3. Keeps the node registry ("stdlib") tiny and explicit, so adding a
     new `uses:` target is obvious by example.
"""

__version__ = "0.1.0"
