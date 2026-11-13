# OpenQWL Specification

Version: Draft 0.2  
Status: Draft  
Copyright (c) 2026 Quantag IT Solutions GmbH  
License: Apache License 2.0

---

# 1. Introduction

OpenQWL, the Open Quantum Workflow Language, is an open, vendor-neutral, YAML-based language for describing complete quantum computing workflows.

Unlike OpenQASM, which represents quantum circuits, OpenQWL represents complete computational experiments.

OpenQWL may reference, generate, import, export, or execute OpenQASM circuits, but it operates at a higher workflow level.

OpenQWL is independent of:

- quantum SDKs
- hardware vendors
- cloud providers
- execution environments

Its purpose is to make quantum workflows portable, reproducible, inspectable, shareable, and suitable for both research and engineering use.

---

# 2. Design Goals

OpenQWL is designed to be:

- human-readable
- declarative
- vendor-neutral
- hardware-independent
- reproducible
- versioned
- extensible
- graph-oriented
- suitable for research and production workflows

---

# 3. Scope

OpenQWL describes:

- computational problems
- workflow graphs
- classical preprocessing
- formal model generation
- quantum algorithms
- hybrid workflows
- execution configuration
- benchmarking
- reporting
- imports and exports

OpenQWL does not describe individual quantum gates directly.

Gate-level circuits should be represented using OpenQASM, QIR, or another supported circuit representation.

---

# 4. Document Structure

An OpenQWL document is a YAML document with the following top-level sections:

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

Only `openqwl`, `metadata`, and `workflow` are required in Draft 0.2.

Other sections are optional but recommended for reproducible workflows.

---

# 5. Versioning

Every OpenQWL document SHALL declare the OpenQWL language version.

Example:

```yaml
openqwl: "0.1"
```

Draft 0.2 documents SHALL use:

```yaml
openqwl: "0.2"
```

Draft 0.2 is backward compatible with Draft 0.1. Every valid Draft 0.1 document remains valid. A document that uses any feature introduced in Draft 0.2 (composite nodes, kernels, execution tiers, targets) SHALL declare `openqwl: "0.2"`.

Future versions SHOULD remain backward compatible when possible.

---

# 6. File Format

OpenQWL documents SHALL be encoded as UTF-8 text.

The document syntax SHALL conform to YAML 1.2.

OpenQWL documents SHOULD use the `.openqwl` file extension.

Examples:

```text
bell.openqwl
maxcut.openqwl
portfolio.openqwl
vqe_h2.openqwl
```

---

# 7. Media Type

The media type for OpenQWL documents is:

```text
application/openqwl
```

OpenQWL documents SHOULD be transferred using:

```text
Content-Type: application/openqwl
```

Future revisions MAY define structured syntax suffixes if required.

---

# 8. Character Encoding

OpenQWL documents SHALL use UTF-8.

Implementations SHOULD accept both LF and CRLF line endings.

---

# 9. Comments

Since OpenQWL is YAML-based, comments SHALL follow YAML syntax.

Example:

```yaml
# Build Bell-state circuit
- id: create_bell
  uses: openqwl://stdlib/circuits/bell
```

---

# 10. Metadata

The `metadata` section describes the workflow document.

Example:

```yaml
metadata:
  id: maxcut-qaoa
  name: MaxCut using QAOA
  version: "1.0"
  author: Quantag IT Solutions GmbH
  description: QAOA workflow for MaxCut.
  created: 2026-07-01
  license: Apache-2.0
```

Recommended fields:

- `id`
- `name`
- `version`
- `author`
- `description`
- `created`
- `license`

The `name` and `version` fields are required in Draft 0.1.

---

# 11. Problem

The `problem` section identifies the computational task.

Example:

```yaml
problem:
  domain: optimization
  type: maxcut
  complexity: NP-hard
  formal_model: QUBO
```

The `problem` section is descriptive.

It does not define execution.

Recommended fields:

- `domain`
- `type`
- `complexity`
- `formal_model`

---

# 12. Imports

The `imports` section describes external input resources.

Examples:

```yaml
imports:
  graph:
    format: edge_list
    path: data/graph.csv
    weighted: true

  circuit:
    format: openqasm3
    path: circuits/bell.qasm

  molecule:
    format: xyz
    path: data/h2.xyz
```

Imports MAY reference local files, remote files, package resources, datasets, or implementation-specific sources.

---

# 13. Workflow

The `workflow` section defines a directed acyclic graph.

A workflow contains:

```yaml
workflow:
  nodes:
  edges:
```

`nodes` is required.

`edges` is optional for single-node workflows, but SHOULD be present for clarity.

Example:

```yaml
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
```

---

# 14. Workflow Semantics

An OpenQWL workflow is a DAG.

Each node performs one operation.

Edges define data flow between nodes.

Execution order is determined by graph dependencies.

No implicit data connections exist.

A compliant implementation SHALL reject workflows with cycles.

Repetition is not expressed with cycles. It is expressed with a composite node (section 14.1) whose body is itself a DAG. Every graph in a document, at every level of nesting, is acyclic.

## 14.1 Composite Nodes

A composite node contains a nested workflow in its `body` field. Draft 0.2 defines two composite components in the reserved `openqwl://core/` namespace.

| Component | Meaning |
|---|---|
| `openqwl://core/group` | Executes its body once. Used to give several nodes a common execution tier or target, for example one session. |
| `openqwl://core/loop` | Executes its body repeatedly until a stop condition holds or an iteration limit is reached. |

A `body` contains:

```yaml
body:
  nodes:      # required, same rules as workflow.nodes
  edges:      # optional, same rules as workflow.edges
  results:    # required for core/loop, optional for core/group
  carry:      # core/loop only
```

### Scoping

- The composite node's `inputs` bind outer variables to port names. Inside the body these port names are readable as variables.
- Body nodes MAY also read variables of the enclosing scope by name.
- Variables produced inside the body are local to the body and are not visible outside it.
- `results` maps each port listed in the composite node's `outputs` to a body variable. After the body completes, the value of that body variable is published to the outer variable named in `outputs`.
- Node identifiers SHALL be unique within one body. A body node MAY reuse an identifier used outside the body.

### Loop semantics

A `core/loop` node SHALL declare `parameters.max_iterations`, a positive integer. It MAY declare `parameters.until`.

```yaml
parameters:
  max_iterations: 200
  until:
    variable: delta      # a body variable
    lt: 1.0e-6           # one of: lt, le, gt, ge, eq
```

Execution of a loop:

1. Each loop variable (port in `inputs`) is initialised from the bound outer variable.
2. The body is executed as a DAG.
3. If `until` is present and its condition holds for the body variable, the loop stops.
4. Otherwise, every entry in `carry` replaces the loop variable named by its key with the body variable named by its value, and the next iteration starts.
5. The loop also stops after `max_iterations` iterations.
6. When the loop stops, `results` are published from the last completed iteration.

Every key in `carry` SHALL be a port declared in the loop node's `inputs`.

Example:

```yaml
- id: vqe_loop
  uses: openqwl://core/loop
  inputs:
    params: theta0
  outputs:
    energy: E
    params: theta
  parameters:
    max_iterations: 200
    until:
      variable: delta
      lt: 1.0e-6
  constraints:
    tier: session
  body:
    nodes:
      - id: estimate
        uses: openqwl://stdlib/chemistry/estimate_energy
        inputs:
          hamiltonian: H
          ansatz: A
          params: params
        outputs:
          energy: e_iter
      - id: update
        uses: openqwl://stdlib/optimization/optimizer_step
        inputs:
          params: params
          energy: e_iter
        outputs:
          params: params_next
          delta: delta
    edges:
      - from: estimate
        to: update
        output: energy
        input: energy
    carry:
      params: params_next
    results:
      energy: e_iter
      params: params_next
```

---

# 15. Node

A node represents one computational operation.

Each node SHALL contain:

```yaml
id:
uses:
```

A node MAY contain:

```yaml
inputs:
outputs:
parameters:
metadata:
capabilities:
constraints:
kernel:      # Draft 0.2, see section 16.8
body:        # Draft 0.2, composite nodes only, see section 14.1
```

Example:

```yaml
- id: build_qaoa
  uses: openqwl://stdlib/optimization/qaoa
  inputs:
    hamiltonian: H
  outputs:
    circuit: C
  parameters:
    p: 2
    optimizer: COBYLA
```

Node identifiers SHALL be unique within a workflow.

---

# 16. Node Fields

## 16.1 id

The `id` field uniquely identifies a node inside a workflow.

Example:

```yaml
id: build_qubo
```

## 16.2 uses

The `uses` field references a reusable OpenQWL component.

It SHOULD use the `openqwl://` URI namespace.

Example:

```yaml
uses: openqwl://stdlib/optimization/qaoa
```

## 16.3 inputs

The `inputs` field declares named inputs consumed by the node.

Example:

```yaml
inputs:
  hamiltonian: H
```

## 16.4 outputs

The `outputs` field declares named outputs produced by the node.

Example:

```yaml
outputs:
  circuit: C
```

## 16.5 parameters

The `parameters` field contains static configuration values.

Example:

```yaml
parameters:
  p: 2
  optimizer: COBYLA
  maxiter: 100
```

## 16.6 capabilities

The `capabilities` field declares execution capabilities.

Example:

```yaml
capabilities:
  - classical
  - quantum
  - hybrid
```

## 16.7 constraints

The `constraints` field declares implementation or execution constraints.

Example:

```yaml
constraints:
  minimum_qubits: 4
  supports_shots: true
```

Draft 0.2 defines three constraint keys with fixed meaning:

| Key | Values | Meaning |
|---|---|---|
| `tier` | `queued`, `session`, `realtime`, `auto` | Required execution tier of the node (section 20.1). Default `auto`. |
| `requires` | list of capability names | Capabilities the selected backend SHALL provide (section 20.2). |
| `target` | target identifier | Pins the node to a target declared in `execution.targets` (section 20.3). |

A constraint on a composite node applies to its whole body. A body node SHALL NOT declare a `target` different from the target of its enclosing composite node. Inside a composite node with `tier: session`, a body node SHALL NOT declare `tier: queued`; it MAY declare `tier: realtime` for a kernel that runs within the session.

## 16.8 kernel

The `kernel` field attaches a quantum program to a node. A kernel is the unit that runs on a quantum device, including any real-time classical logic such as branching on mid-circuit measurements.

OpenQWL does not define kernel syntax. Kernels are written in an existing kernel language and referenced or embedded.

```yaml
kernel:
  format: openqasm3          # openqasm2 | openqasm3 | qir-base | qir-adaptive | vendor URI
  source: kernels/teleport.qasm
```

or

```yaml
kernel:
  format: openqasm3
  inline: |
    OPENQASM 3.0;
    ...
```

Exactly one of `source` and `inline` SHALL be present. `source` is a relative path or a URI.

A node whose only purpose is to execute a kernel SHALL use `uses: openqwl://core/kernel`. Other components MAY also accept a `kernel` field.

## 16.9 body

The `body` field is defined only for composite nodes. See section 14.1.

---

# 17. Edge

An edge connects the output of one node to the input of another node.

Each edge SHALL contain:

```yaml
from:
to:
output:
input:
```

Example:

```yaml
edges:
  - from: build_ising
    to: build_qaoa
    output: hamiltonian
    input: hamiltonian
```

The `from` and `to` fields SHALL reference existing node identifiers.

The `output` field SHALL reference an output name declared by the source node.

The `input` field SHALL reference an input name declared by the target node.

---

# 18. Type System

OpenQWL workflows pass typed semantic objects between nodes.

Examples:

```text
Graph
QUBO
IsingModel
Hamiltonian
Circuit
OpenQASM
Counts
StateVector
Solution
Report
```

Draft 0.1 defines the type system in `TYPE_SYSTEM.md`.

Validators SHOULD reject incompatible node connections when type declarations are available.

Example valid flow:

```text
Graph → QUBO → IsingModel → Hamiltonian → Circuit → Counts → Solution
```

Example invalid flow:

```text
Circuit → QUBO Builder
```

---

# 19. Standard Library

OpenQWL defines reusable standard components under the standard library namespace:

```text
openqwl://stdlib/
```

Examples:

```text
openqwl://stdlib/circuits/bell
openqwl://stdlib/optimization/qaoa
openqwl://stdlib/optimization/maxcut/to_qubo
openqwl://stdlib/optimization/qubo/to_ising
openqwl://stdlib/chemistry/vqe
openqwl://stdlib/export/qasm
openqwl://stdlib/report/json
```

The standard library may include:

- circuits
- optimization
- chemistry
- finance
- benchmark
- report
- debug
- visualization
- import
- export

---

# 20. Execution

The `execution` section defines runtime configuration.

Example:

```yaml
execution:
  runtime:
    uses: openqwl://runtime/qiskit
    version: ">=1.0"

  backend:
    provider: ibm
    target: ibm_brisbane

  shots: 4096
  optimization_level: 3
  seed: 1234
```

Execution engines MAY ignore unsupported parameters, but SHOULD report warnings.

Draft 0.2 adds the keys `tier` and `targets` to the `execution` section.

```yaml
execution:
  tier: auto                 # default for every node; queued | session | realtime | auto
  targets:
    - id: qpu_a
      uses: openqwl://hardware/site_a/qpu_1
      access: [qrmi, qdmi]   # qdmi | qrmi | native | simulator | auto, or a composition
    - id: local
      uses: openqwl://hardware/local/simulator
      access: simulator
```

## 20.1 Execution Tiers

The tier states how quickly classical code must respond to quantum results. It does not rank the quality of a method.

| Tier | Response time | Where classical code runs | Typical use |
|---|---|---|---|
| `queued` | minutes to hours | anywhere | single circuits, batches, sweeps |
| `session` | milliseconds to seconds per iteration | next to the QPU, within one reservation of the device | variational loops |
| `realtime` | within the coherence time | on the control system of the device | feed-forward on mid-circuit measurements |
| `auto` | | chosen by the implementation | default |

Rules:

1. `realtime` SHALL only be declared on a node that carries a `kernel`. Real-time logic is part of the kernel and is never expressed as workflow nodes or edges.
2. `session` on a composite node means that its whole body SHALL be executed within one reservation of the target device.
3. With `auto`, an implementation chooses the tier. It SHOULD choose `realtime` for kernels that branch on mid-circuit measurements, and SHOULD consider `session` for a `core/loop` whose body contains a quantum node, taking latency, queue behaviour and cost into account.
4. A node's `constraints.tier` overrides `execution.tier`.

Fallback:

- If `session` is requested and the target offers no sessions, an implementation MAY execute the body as `queued` jobs and SHALL report a warning. It SHALL preserve the workflow semantics. Results on physical hardware MAY differ, because the device can change between jobs.
- If `realtime` is requested and the target cannot execute the kernel in real time, an implementation SHALL report an error and SHALL NOT fall back.

## 20.2 Capability Names

The following names are defined for `constraints.requires`:

| Name | Meaning |
|---|---|
| `mid_circuit_measurement` | Measurement of a qubit before the end of the kernel. |
| `feed_forward` | Later operations depend on earlier measurement results within one kernel execution. |
| `qubit_reuse` | A measured qubit can be reset and used again. |
| `sessions` | The device can be reserved for a sequence of jobs. |

Implementations MAY accept additional names. Unknown names SHALL cause a warning, not an error.

## 20.3 Targets

`execution.targets` lists the resources a workflow may run on. Each target SHALL have an `id` and a `uses` URI (section 23.3). The optional `access` field selects how the device is reached:

| Value | Meaning |
|---|---|
| `qdmi` | Through the Quantum Device Management Interface. |
| `qrmi` | Through the Quantum Resource Management Interface. |
| `native` | Through the provider's own SDK or API. |
| `simulator` | A local or emulated simulator. |
| `auto` | Chosen by the implementation. Default. |

A list such as `[qrmi, qdmi]` composes two paths: the first acquires the resource and the second operates the device.

A node is pinned to a target with `constraints.target`. Without it, the implementation selects a target that satisfies the node's tier and `requires`.

Access selection does not change the meaning of a workflow. A document SHALL produce the same logical results on any target that satisfies its constraints.

---

# 21. Exports

The `exports` section defines generated artifacts.

Example:

```yaml
exports:
  qasm:
    format: openqasm3
    path: output/maxcut.qasm

  report:
    format: json
    path: output/report.json

  plot:
    format: png
    path: output/result.png
```

Exports SHOULD be reproducible from the workflow, imports, parameters, and execution configuration.

---

# 22. Metrics

The `metrics` section defines observable outputs.

Example:

```yaml
metrics:
  - runtime
  - gate_count
  - circuit_depth
  - approximation_ratio
  - fidelity
  - cloud_cost
```

Metrics are implementation-independent names unless explicitly namespaced.

---

# 23. URI Namespace

OpenQWL defines the canonical URI namespace:

```text
openqwl://
```

All globally identifiable OpenQWL resources SHOULD use this namespace.

The namespace is reserved by the OpenQWL specification.

---

## 23.0 Core

The `openqwl://core/` namespace is reserved for components defined by this specification: `core/group`, `core/loop` and `core/kernel`. Other components SHALL NOT be published in this namespace.

## 23.1 Standard Library

```text
openqwl://stdlib/
```

Examples:

```text
openqwl://stdlib/circuits/bell
openqwl://stdlib/optimization/qaoa
openqwl://stdlib/optimization/maxcut
openqwl://stdlib/chemistry/vqe
openqwl://stdlib/report/pdf
```

---

## 23.2 Runtime

```text
openqwl://runtime/
```

Examples:

```text
openqwl://runtime/qiskit
openqwl://runtime/pennylane
openqwl://runtime/cirq
openqwl://runtime/cudaq
openqwl://runtime/braket
```

---

## 23.3 Hardware

```text
openqwl://hardware/
```

Examples:

```text
openqwl://hardware/ibm/brisbane
openqwl://hardware/ionq/aria
openqwl://hardware/rigetti/ankaa
openqwl://hardware/dwave/advantage
```

---

## 23.4 Dataset

```text
openqwl://dataset/
```

Example:

```text
openqwl://dataset/maxcut/gset/G1
```

---

## 23.5 Benchmark

```text
openqwl://benchmark/
```

Example:

```text
openqwl://benchmark/maxcut/approximation_ratio
```

---

## 23.6 Vendor

```text
openqwl://vendor/
```

Examples:

```text
openqwl://vendor/ibm/error_mitigation
openqwl://vendor/quantag/gem_optimizer
```

---

## 23.7 Community

```text
openqwl://community/
```

Example:

```text
openqwl://community/example/custom_optimizer
```

---

## 23.8 User

```text
openqwl://user/
```

Example:

```text
openqwl://user/my_company/my_pipeline
```

---

# 24. URI Resolution

URI resolution is implementation-dependent.

Implementations MAY resolve resources:

- locally
- from package registries
- from Git repositories
- from cloud registries
- from embedded standard libraries

OpenQWL does not define a package transport protocol in Draft 0.1.

---

# 25. Vendor Extensions

Implementations MAY define vendor-specific extensions.

Vendor extensions SHALL be namespaced.

Example:

```yaml
vendor:
  ibm:
    resilience_level: 2

  quantag:
    optimization_strategy: gem_v1
```

Unknown vendor extensions SHALL be ignored by compliant parsers unless strict mode is enabled.

---

# 26. Validation

An OpenQWL document is valid when:

- required sections exist
- the document declares a supported OpenQWL version
- metadata contains required fields
- workflow contains nodes
- all node identifiers are unique
- all edges reference existing nodes
- all referenced outputs exist
- all referenced inputs exist
- the workflow graph contains no cycles
- every composite body satisfies the same rules, recursively
- every `core/loop` node declares a positive `max_iterations`
- every `carry` key is a port declared in the loop node's `inputs`
- every `results` key is a port declared in the composite node's `outputs`
- every node that declares `tier: realtime` carries a `kernel`
- every `kernel` has a `format` and exactly one of `source` and `inline`
- every `constraints.target` references a declared target
- no body node contradicts the `tier` or `target` of its enclosing composite node
- the document conforms to the published schema

A validator SHOULD produce actionable error messages.

Example:

```text
Invalid edge:
  from: build_qaoa
  output: hamiltonian

Reason:
  node build_qaoa does not declare output hamiltonian
```

---

# 27. Compliance

An implementation is OpenQWL Draft 0.2 compliant if it:

- parses valid OpenQWL documents
- validates required structure
- preserves workflow graph semantics
- reports validation errors
- supports the `.openqwl` file extension
- accepts UTF-8 YAML 1.2 input
- validates composite nodes, kernels, tiers and targets as defined in sections 14.1, 16.7, 16.8 and 20

An implementation MAY reject tiers or targets it cannot execute, but SHALL report which constraint it cannot satisfy.

Additional capabilities MAY be implemented.

---

# 28. Compatibility

OpenQWL implementations MAY support adapters for:

- OpenQASM 3
- QIR
- Qiskit
- PennyLane
- Cirq
- CUDA-Q
- Amazon Braket
- Classiq
- IBM Quantum
- D-Wave
- Quantinuum
- IonQ

Support is implementation-dependent.

---

# 29. Minimal Valid Document

```yaml
openqwl: "0.1"

metadata:
  name: Minimal OpenQWL Document
  version: "1.0"

workflow:
  nodes: []
  edges: []
```

This document is valid but not executable.

---

# 30. Complete Example

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

# 31. Relationship to OpenQASM

OpenQASM is a circuit language.

OpenQWL is a workflow language.

OpenQWL may:

- import OpenQASM
- export OpenQASM
- generate OpenQASM
- execute OpenQASM
- include OpenQASM as an artifact

OpenQWL does not replace OpenQASM.

---

# 32. Future Work

Future versions may define:

- workflow composition
- reusable modules
- package manager
- remote registry
- variables
- conditionals at workflow level (conditionals on measurement results are expressed inside kernels)
- distributed execution across linked devices (links between targets)
- workflow optimization
- execution provenance
- experiment databases
- signed workflows
- compliance test suites

---

# 33. License

This specification is distributed under the Apache License 2.0.

Copyright (c) 2026 Quantag IT Solutions GmbH.

OpenQWL is a trademark of Quantag IT Solutions GmbH.