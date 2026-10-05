#!/usr/bin/env python3
"""CLI utility to generate or display an experiment report."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation.reporter import ExperimentReporter
from runtime.registry.registry import ExperimentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate experiment report.")
    parser.add_argument("experiment_id", type=str, help="Experiment ID (e.g., EXP-000001).")
    parser.add_argument("--save", type=str, default=None, help="Save markdown report to custom path.")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    record = registry.get(args.experiment_id)
    if not record:
        print(f"Error: Experiment {args.experiment_id} not found.", file=sys.stderr)
        sys.exit(1)

    md = ExperimentReporter.generate_markdown(record)
    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Report saved to {args.save}")
    else:
        print(md)


if __name__ == "__main__":
    main()
