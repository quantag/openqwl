# OpenQWL Specification

Version: Draft 0.1

Status: Draft

Copyright (c) 2026 Quantag IT Solutions GmbH

License: Apache License 2.0

---

# 1. Introduction

OpenQWL (Open Quantum Workflow Language) is an open, vendor-neutral,
YAML-based language for describing complete quantum computing workflows.

Unlike OpenQASM, which represents quantum circuits, OpenQWL represents
entire computational experiments.

OpenQWL is independent of:

- quantum SDKs
- hardware vendors
- cloud providers
- execution environments

Its purpose is to make quantum workflows portable,
reproducible,
inspectable,
and shareable.

---

# 2. Design Goals

OpenQWL has the following goals.

• Human-readable

• Declarative

• Vendor-neutral

• Hardware-independent

• Reproducible

• Versioned

• Extensible

• Graph-oriented

• Suitable for research and production

---

# 3. Scope

OpenQWL describes

- computational problems

- workflow graphs

- preprocessing

- classical algorithms

- quantum algorithms

- hybrid workflows

- execution environments

- benchmarking

- reporting

OpenQWL does NOT describe individual quantum gates.

Quantum circuits are represented using OpenQASM or another supported
circuit language.

---

# 4. Document Structure

Every OpenQWL document consists of the following sections.

```yaml
openqwl:
metadata:
problem:
imports:
workflow:
execution:
exports:
metrics:
```

Additional sections MAY be introduced by future versions.

---

# 5. Versioning

Every document SHALL declare the language version.

Example

```yaml
openqwl: "0.1"
```

Future versions MUST remain backward compatible whenever possible.

---

# 6. Metadata

Metadata describes the workflow.

Example

```yaml
metadata:

  id: maxcut-qaoa

  name: MaxCut using QAOA

  version: "1.0"

  author: Quantag IT Solutions GmbH

  description: Example workflow

  created: 2026-07-01

  license: Apache-2.0
```

---

# 7. Problem

The problem section identifies the computational task.

Example

```yaml
problem:

  domain: optimization

  type: maxcut

  complexity: NP-hard

  formal_model: QUBO
```

This section is descriptive only.

It does not define execution.

---

# 8. Imports

Imports describe external data.

Example

```yaml
imports:

  graph:

    format: edge_list

    path: data/graph.csv

  circuit:

    format: openqasm3

    path: bell.qasm
```

Supported formats are implementation-dependent.

---

# 9. Workflow

A workflow is a directed acyclic graph (DAG).

Each node performs exactly one operation.

Nodes are connected by named inputs and outputs.

---

## 9.1 Node

Each node SHALL contain

```yaml
id:
uses:
inputs:
outputs:
parameters:
```

Example

```yaml
- id: qaoa

  uses: stdlib.optimization.qaoa

  inputs:

    hamiltonian: h1

  outputs:

    circuit: c1

  parameters:

    p: 2

    optimizer: COBYLA
```

---

## 9.2 Connections

Outputs are connected to inputs.

Example

```yaml
inputs:

    hamiltonian: build_hamiltonian.output
```

No implicit connections exist.

---

## 9.3 Standard Node Types

Examples

```
data.load

qubo.build

ising.convert

qaoa

vqe

grover

execute

benchmark

report
```

Future implementations MAY introduce additional node types.

---

# 10. Standard Library

OpenQWL defines a reusable standard library.

Example

```
stdlib/

optimization/

chemistry/

finance/

circuits/

benchmark/

report/
```

Nodes reference standard components through

```
uses:
```

Example

```yaml
uses: stdlib.optimization.qaoa
```

---

# 11. Execution

Execution describes where the workflow is executed.

Example

```yaml
execution:

  backend:

    provider: ibm

    target: ibm_brisbane

  shots: 4096

  optimization_level: 3
```

Execution engines MAY ignore unsupported parameters.

---

# 12. Exports

Exports define generated artifacts.

Example

```yaml
exports:

  report:

    format: pdf

    path: report.pdf

  qasm:

    format: openqasm3

    path: output.qasm
```

---

# 13. Metrics

Metrics define observable outputs.

Example

```yaml
metrics:

- approximation_ratio

- runtime

- gate_count

- circuit_depth

- fidelity
```

Metrics are implementation-independent.

---

# 14. Validation

An OpenQWL document is valid when

- required sections exist

- all node identifiers are unique

- the workflow graph contains no cycles

- referenced inputs exist

- referenced outputs exist

- the document conforms to the published schema

---

# 15. Vendor Extensions

Implementations MAY define vendor-specific extensions.

Vendor extensions SHALL be namespaced.

Example

```yaml
vendor:

  ibm:

    resilience_level: 2
```

Unknown vendor extensions SHALL be ignored by compliant parsers.

---

# 16. Compatibility

OpenQWL implementations SHOULD support

- OpenQASM 3

- Qiskit

- PennyLane

- Cirq

- CUDA-Q

- Amazon Braket

Support is implementation-dependent.

---

# 17. Compliance

An implementation is OpenQWL compliant if it

- parses valid documents

- validates schema

- preserves workflow semantics

- reports validation errors

Additional capabilities MAY be implemented.

---

# 18. Future Work

Future versions may define

- workflow composition

- reusable modules

- variables

- conditionals

- loops

- distributed execution

- workflow optimization

- execution provenance

- experiment databases

---

# 19. License

This specification is distributed under the Apache License 2.0.

Copyright (c) 2026 Quantag IT Solutions GmbH.

OpenQWL is a trademark of Quantag IT Solutions GmbH.