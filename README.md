# OpenQWL

**Open Quantum Workflow Language**

OpenQWL is an open, vendor-neutral YAML-based language for describing complete quantum computing workflows.

Unlike OpenQASM, which describes quantum circuits, OpenQWL describes the full computational workflow around a quantum experiment:

- problem definition
- data import
- classical preprocessing
- formal model generation
- quantum algorithm construction
- execution
- post-processing
- benchmarking
- reporting

OpenQWL is designed to make quantum workflows portable, reproducible, inspectable, and independent of any single SDK or hardware vendor.

---

## Why OpenQWL?

Quantum computing workflows are usually scattered across Python scripts, notebooks, SDK-specific code, configuration files, and manual experiment notes.

OpenQWL provides one declarative workflow format for the whole experiment.

```text
Problem
  ↓
Imports
  ↓
Workflow DAG
  ↓
Execution
  ↓
Exports
  ↓
Metrics
```

OpenQASM describes circuits.

OpenQWL describes workflows.

---

## Principles

- Human-readable
- YAML-based
- Vendor-neutral
- Graph-oriented
- Reproducible
- Versioned
- Extensible
- Suitable for research and engineering workflows

---

## File Extension

OpenQWL documents should use the `.openqwl` file extension.

Examples:

```text
bell.openqwl
maxcut.openqwl
vqe_h2.openqwl
```

The document syntax is YAML 1.2.

Recommended media type:

```text
application/openqwl
```

---

## Minimal Example

```yaml
openqwl: "0.1"

metadata:
  id: bell-state
  name: Bell State Workflow
  version: "1.0"
  author: Quantag IT Solutions GmbH
  license: Apache-2.0

problem:
  domain: circuits
  type: bell_state
  formal_model: quantum_circuit

workflow:
  nodes:
    - id: create_bell
      uses: openqwl://stdlib/circuits/bell
      outputs:
        circuit: bell_circuit
      parameters:
        qubits: 2

    - id: export_qasm
      uses: openqwl://stdlib/export/qasm
      inputs:
        circuit: bell_circuit
      outputs:
        file: bell_qasm
      parameters:
        format: openqasm3
        path: output/bell.qasm

  edges:
    - from: create_bell
      to: export_qasm
      output: circuit
      input: circuit

exports:
  qasm:
    format: openqasm3
    path: output/bell.qasm

metrics:
  - qubit_count
  - gate_count
  - circuit_depth
```

---

## Repository Structure

```text
openqwl/
  README.md
  SPEC.md
  VOCABULARY.md
  REGISTRY.md
  NODE_SPEC.md
  TYPE_SYSTEM.md
  ARCHITECTURE.md
  GOVERNANCE.md
  TRADEMARK.md
  CONTRIBUTING.md
  LICENSE

  schema/
    openqwl.schema.json

  examples/
    bell.openqwl
    maxcut.openqwl
    vqe_h2.openqwl

  stdlib/
    circuits/
    optimization/
    chemistry/
    benchmark/
    report/

  reference/
    python/
```

---

## Status

OpenQWL is currently in **Draft 0.1**.

The current goal is to define:

- core document structure
- graph-based workflow model
- URI namespace
- node model
- type system
- schema validation
- first executable examples

---

## License

OpenQWL is distributed under the Apache License 2.0.

Copyright (c) 2026 Quantag IT Solutions GmbH.

---

## Trademark

OpenQWL is a trademark of Quantag IT Solutions GmbH.

See `TRADEMARK.md`.