# OpenQWL Architecture

Version: Draft 0.1  
Status: Draft  
Copyright (c) 2026 Quantag IT Solutions GmbH  
License: Apache License 2.0

---

# 1. Purpose

OpenQWL is designed to describe complete quantum computing workflows.

It does not replace OpenQASM.

OpenQASM describes quantum circuits.  
OpenQWL describes experiments, pipelines, execution, outputs, and reproducibility.

---

# 2. Core Architecture

```text
Problem
   │
   ▼
Imports
   │
   ▼
Workflow DAG
   │
   ▼
Execution
   │
   ▼
Exports
   │
   ▼
Metrics