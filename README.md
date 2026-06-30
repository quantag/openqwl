# OpenQWL

**Open Quantum Workflow Language**

OpenQWL is an open, vendor-neutral YAML language for describing complete quantum computing workflows.

Unlike OpenQASM, which describes quantum circuits, OpenQWL describes the entire computational workflow, including:

- Problem definition
- Data import
- Classical preprocessing
- Formal model generation (QUBO, Ising, Hamiltonian, ...)
- Quantum algorithm execution
- Classical post-processing
- Benchmarking
- Reporting

The goal of OpenQWL is to make quantum workflows portable, reproducible and independent of any particular SDK or hardware vendor.

## Principles

- Human readable
- YAML based
- Vendor neutral
- Reproducible
- Extensible
- Versioned
- Open standard

## Example

```yaml
openqwl: "0.1"

problem:
  type: optimization.maxcut

workflow:
  - uses: stdlib.optimization.qaoa