#!/usr/bin/env python3
"""CLI utility to compare two experiments from the registry."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation.comparison import ExperimentComparator
from runtime.registry.registry import ExperimentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two experiment records.")
    parser.add_argument("exp1", type=str, help="First Experiment ID (e.g., EXP-000001).")
    parser.add_argument("exp2", type=str, help="Second Experiment ID (e.g., EXP-000002).")
    parser.add_argument("--markdown", action="store_true", help="Print full Markdown comparison report.")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    r1 = registry.get(args.exp1)
    r2 = registry.get(args.exp2)

    if not r1:
        print(f"Error: Experiment {args.exp1} not found.", file=sys.stderr)
        sys.exit(1)
    if not r2:
        print(f"Error: Experiment {args.exp2} not found.", file=sys.stderr)
        sys.exit(1)

    comp = ExperimentComparator.compare(r1, r2)

    if args.markdown:
        print(ExperimentComparator.generate_markdown_report(comp))
        return

    print("=" * 60)
    print(f" COMPARISON: {args.exp1} vs {args.exp2}")
    print("=" * 60)
    print(f"Verdict                  : {comp.reproducibility_verdict}")
    print(f"Bitwise Identical Output : {comp.bitwise_identical_output}")
    print(f"Seeds Match              : {comp.seeds_match}")
    print(f"Config Match             : {comp.configurations_match}")
    print(f"Hardware Match           : {comp.hardware_fingerprints_match}")
    print(f"Duration Diff            : {comp.duration_diff.delta:+.4f} s ({comp.duration_diff.pct_delta:+.2f}%)")
    print(f"Peak RSS Diff            : {comp.peak_rss_diff.delta / (1024**2):+.2f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()
