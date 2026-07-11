"""
Command-line entry point.

Usage:
    python -m openqwl run examples/bell.openqwl
    openqwl run examples/bell.openqwl        (if installed via pip install -e .)
"""

from __future__ import annotations

import argparse
import sys

from .backends import backend_name
from .executor import ExecutionError, collect_metrics, run
from .parser import OpenQWLValidationError, load_workflow
from .registry import UnknownNodeError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openqwl")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute a .openqwl workflow")
    run_parser.add_argument("path", help="Path to a .openqwl file")

    args = parser.parse_args(argv)

    if args.command == "run":
        return _run(args.path)

    return 1


def _run(path: str) -> int:
    print(f"OpenQWL reference runner (circuit backend: {backend_name()})")
    print(f"Loading {path} ...")

    try:
        doc = load_workflow(path)
    except (FileNotFoundError, OpenQWLValidationError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"  openqwl version : {doc.version}")
    print(f"  workflow id      : {doc.metadata.get('id', '(none)')}")
    print(f"  nodes            : {len(doc.nodes)}")

    try:
        result = run(doc)
    except (ExecutionError, UnknownNodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"\nExecuted nodes in order: {' -> '.join(result.node_order)}")

    if result.exported_files:
        print("\nExported files:")
        for f in result.exported_files:
            print(f"  - {f}")

    metrics = collect_metrics(doc, result)
    if metrics:
        print("\nMetrics:")
        for circuit_name, values in metrics.items():
            print(f"  {circuit_name}:")
            for k, v in values.items():
                print(f"    {k}: {v}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
