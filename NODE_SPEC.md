# OpenQWL Node Specification

Version: Draft 0.2

A node represents exactly one computational operation.

Nodes SHALL be side-effect free.

---

# Required Fields

id

uses

---

# Optional Fields

inputs

outputs

parameters

metadata

capabilities

constraints

kernel (Draft 0.2: a quantum program in OpenQASM or QIR, see SPEC.md section 16.8)

body (Draft 0.2: composite nodes only, see SPEC.md section 14.1)

---

# Example

- id: qaoa

  uses: openqwl://stdlib/optimization/qaoa

  inputs:

    hamiltonian: H

  outputs:

    circuit: C

  parameters:

    p: 2

---

# Node Lifecycle

receive inputs

↓

validate

↓

execute

↓

produce outputs

---

# Rules

Node identifiers SHALL be unique.

Nodes SHALL NOT modify inputs.

Outputs SHALL be immutable.

Execution order SHALL be determined by graph dependencies.

---

# Capabilities

Examples

classical

quantum

gpu

hybrid

---

# Constraints

Examples

minimum_qubits

required_backend

minimum_memory
