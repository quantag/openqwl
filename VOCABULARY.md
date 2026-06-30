# OpenQWL Vocabulary

Version: Draft 0.1

This document defines the reserved vocabulary of OpenQWL.

Reserved keywords SHALL NOT be redefined.

---

# Document

The root OpenQWL document.

Contains:

- metadata
- problem
- imports
- workflow
- execution
- exports
- metrics

---

# Metadata

Describes the workflow.

Contains information such as

- id
- name
- author
- version
- description
- license

---

# Problem

Describes the computational problem.

Examples

- optimization.maxcut
- optimization.tsp
- chemistry.vqe
- finance.portfolio

---

# Workflow

A directed acyclic graph (DAG).

Contains

- nodes
- edges

---

# Node

A single computational operation.

Every node SHALL define

- id
- uses

Optional

- inputs
- outputs
- parameters
- metadata

---

# Edge

Connects two nodes.

Fields

- from
- to
- output
- input

---

# Input

Named object consumed by a node.

---

# Output

Named object produced by a node.

---

# Parameters

Static configuration values.

Examples

- p
- shots
- optimizer
- backend

---

# Imports

External resources.

Examples

- CSV
- OpenQASM
- XYZ
- JSON

---

# Exports

Generated artifacts.

Examples

- Report
- OpenQASM
- QIR
- PNG

---

# Execution

Defines runtime configuration.

Examples

- backend
- provider
- shots

---

# Metrics

Observable measurements.

Examples

- runtime
- fidelity
- gate_count
- circuit_depth

---

# Uses

Reference to reusable component.

Example

openqwl://stdlib/optimization/qaoa

---

# Capability

Declares supported execution modes.

Examples

- classical
- quantum
- gpu
- hybrid