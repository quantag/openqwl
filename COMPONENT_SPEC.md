openqwl: "0.1"

metadata:
  id: bell
  name: Bell State
  version: "1.0"
  author: OpenQWL Project
  description: Standard Bell state circuit template.
  license: Apache-2.0

component:
  uri: openqwl://stdlib/circuits/bell

  category: circuits

  kind: circuit_template

  summary: |
    Generates a two-qubit Bell state.

  inputs: {}

  outputs:
    circuit:
      type: Circuit
      description: Bell-state quantum circuit.

  parameters:
    qubits:
      type: Integer
      default: 2
      minimum: 2
      maximum: 2
      required: true
      description: Number of qubits.

  capabilities:
    - quantum

  constraints:
    minimum_qubits: 2

implementation:

  operation: bell_state

  equivalent_qasm: |
    OPENQASM 3;
    include "stdgates.inc";

    qubit[2] q;

    h q[0];
    cx q[0], q[1];

  compatible_runtimes:
    - openqwl://runtime/qiskit
    - openqwl://runtime/cirq
    - openqwl://runtime/pennylane
    - openqwl://runtime/cudaq

references:
  - Bell, J. S. (1964)