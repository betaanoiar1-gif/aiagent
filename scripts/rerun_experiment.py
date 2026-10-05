#!/usr/bin/env python3
"""CLI utility to reproduce an existing experiment from its experiment ID."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runtime.runner.reproducibility import ReproducibilityEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce an existing experiment.")
    parser.add_argument("experiment_id", type=str, help="Experiment ID to replicate (e.g., EXP-000001).")
    parser.add_argument("--seed", type=int, default=None, help="Optional override of random seed.")
    args = parser.parse_args()

    engine = ReproducibilityEngine()
    try:
        replica, comparison = engine.reproduce(args.experiment_id, custom_seed=args.seed)
    except Exception as e:
        print(f"Error during reproduction: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print(f" REPRODUCIBILITY RESULTS: {args.experiment_id} -> {replica.experiment_id}")
    print("=" * 60)
    print(f"Verdict                  : {comparison.reproducibility_verdict}")
    print(f"Bitwise Identical Output : {comparison.bitwise_identical_output}")
    print(f"Hardware Match           : {comparison.hardware_fingerprints_match}")
    print(f"Software Match           : {comparison.software_fingerprints_match}")
    print(f"Wall-Clock Duration Diff : {comparison.duration_diff.delta:+.4f} s ({comparison.duration_diff.pct_delta:+.2f}%)")
    print(f"Peak RSS Memory Diff     : {comparison.peak_rss_diff.delta / (1024**2):+.2f} MB")
    print(f"Natural Jitter Observed  : {comparison.natural_jitter_observed}")
    print("-" * 60)
    for note in comparison.analysis_notes:
        print(f" - {note}")
    print("=" * 60)


if __name__ == "__main__":
    main()
