# OpenQWL Standard Library

Version: Draft 0.1

The OpenQWL Standard Library defines reusable workflow components for quantum computing experiments.

A standard library component is not necessarily a complete workflow. It may represent:

- a quantum algorithm
- a circuit template
- a model transformation
- an importer
- an exporter
- a runtime adapter
- a benchmark step
- a reporting step

Components are referenced using the OpenQWL URI namespace.

Example:

```yaml
uses: openqwl://stdlib/optimization/qaoa