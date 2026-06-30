# OpenQWL Type System

Version: Draft 0.1

The OpenQWL type system defines the semantic objects flowing through workflows.

---

# Primitive Types

Integer

Float

Boolean

String

Array

Object

---

# Quantum Types

Circuit

OpenQASM

QIR

StateVector

DensityMatrix

Counts

BitString

Observable

Hamiltonian

Operator

PauliOperator

Measurement

---

# Optimization Types

Graph

QUBO

IsingModel

Solution

ObjectiveFunction

ConstraintSet

---

# Chemistry Types

Molecule

XYZ

BasisSet

Orbital

ElectronicStructure

---

# Machine Learning

Dataset

Tensor

Embedding

FeatureVector

---

# Reports

PDF

JSON

CSV

Image

Plot

---

# Validation

Connections SHALL have compatible types.

Example

Graph

↓

QUBO Builder

↓

QUBO

Valid

---

Example

Circuit

↓

QUBO Builder

Invalid

---

Validators SHALL report

Expected Type

Received Type

Node

Input

Output

---

# Future Extensions

Implementations MAY define custom types.

Custom types SHALL use vendor namespaces.

Example

vendor.quantag.GEMCircuit