# OpenQWL Reference Runner

A minimal, readable interpreter for `.openqwl` workflow documents. It proves
the document model — `problem` / `workflow.nodes` + `workflow.edges` /
`exports` / `metrics` — is executable, not just descriptive.

This is a **reference implementation**, not the final engine for the
language: it hardcodes a small stdlib registry (just enough to run
`examples/bell.openqwl`) instead of resolving `openqwl://` URIs against a
real package registry. See `REGISTRY.md` in the repo root for where that's
headed.

## Install

No dependencies are required to try it:

```bash
cd reference/python
python3 -m openqwl.cli run ../../examples/bell.openqwl
```

For a proper install with the `openqwl` command on your PATH:

```bash
cd reference/python
pip install -e .
openqwl run ../../examples/bell.openqwl
```

Optional extras:

```bash
pip install -e ".[qiskit]"   # real OpenQASM3 export via Qiskit
pip install -e ".[schema]"   # full validation against schema/openqwl.schema.json
```

Without `qiskit` installed, a built-in fallback circuit backend
(`openqwl/backends/simple.py`) is used automatically — it supports exactly
the gates the bundled example needs (`h`, `cx`) and produces valid
OpenQASM 3 text. Install `qiskit` and the runner switches backends with no
changes to your `.openqwl` file, which is the whole point: the same
document should be able to target different execution backends.

## What it does

```
$ openqwl run examples/bell.openqwl

OpenQWL reference runner (circuit backend: simple (built-in, no external dependencies))
Loading examples/bell.openqwl ...
  openqwl version : 0.1
  workflow id      : bell-state
  nodes            : 2

Executed nodes in order: create_bell -> export_qasm

Exported files:
  - output/bell.qasm

Metrics:
  bell_circuit:
    qubit_count: 2
    gate_count: 2
    circuit_depth: 2

Done.
```

## How it works

1. **`parser.py`** loads the YAML and validates required structure (falls
   back gracefully if `jsonschema` isn't installed for full schema
   validation).
2. **`executor.py`** topologically sorts `workflow.nodes` using
   `workflow.edges` (Kahn's algorithm, raises on cycles), then runs each
   node in order, passing outputs to downstream nodes via a shared context
   dict keyed by the global variable names declared in each node's
   `outputs:` mapping.
3. **`registry.py`** maps each node's `uses:` URI to a Python function.
   Currently registered:
   - `openqwl://stdlib/circuits/bell` → builds an n-qubit GHZ/Bell circuit
   - `openqwl://stdlib/export/qasm` → writes OpenQASM 3 to disk
4. **`backends/`** abstracts the actual circuit object so nodes don't care
   whether Qiskit is installed.

## Extending it

To support a new example (e.g. `maxcut.openqwl`), add a function to
`stdlib/` with the signature `(parameters, inputs) -> outputs`, register its
`openqwl://` URI in `registry.py`, and, if it needs a gate the backends
don't support yet, extend `backends/simple.py` and
`backends/qiskit_backend.py` in parallel so both stay in sync.

## Known limitations (by design, for now)

- Only two stdlib nodes are implemented — enough to prove the model works,
  not a general engine yet.
- No conditional/branching workflow support — `workflow.edges` is a plain
  DAG.
- `SimpleCircuit` is not a simulator; it only tracks gate structure for
  metrics and OpenQASM3 export.
- Only `qasm`/`openqasm3` export is supported.

Contributions extending the registry are welcome — see `CONTRIBUTING.md`.
