#!/usr/bin/env python3
"""CLI utility to launch an experiment using the Benchmark Runner."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runtime.config.experiment_config import ExperimentConfig
from runtime.config.runtime_config import RuntimeConfig
from runtime.runner.runner import BenchmarkRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a scientific experiment.")
    parser.add_argument("--config", type=str, help="Path to experiment config JSON file.")
    parser.add_argument("--name", type=str, default="cli-experiment", help="Experiment name.")
    parser.add_argument("--hypothesis", type=str, default="Baseline execution verification.", help="Hypothesis.")
    parser.add_argument("--objective", type=str, default="Validate runner pipeline.", help="Objective.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--iterations", type=int, default=1000, help="Workload iterations.")
    parser.add_argument("--matrix-size", type=int, default=64, help="Synthetic matrix size.")
    parser.add_argument("--simulate-failure", action="store_true", help="Simulate execution failure.")
    parser.add_argument("--failure-message", type=str, default="Simulated failure from CLI", help="Failure message.")
    parser.add_argument("--notes", type=str, default="", help="Experimental notes.")
    args = parser.parse_args()

    if args.config:
        config = ExperimentConfig.from_json_file(args.config)
    else:
        workload_params = {
            "iterations": args.iterations,
            "matrix_size": args.matrix_size,
        }
        if args.simulate_failure:
            workload_params["simulate_failure"] = True
            workload_params["failure_message"] = args.failure_message

        config = ExperimentConfig(
            experiment_name=args.name,
            hypothesis=args.hypothesis,
            objective=args.objective,
            model_identifier="synthetic-baseline-v0",
            model_revision="v0.1",
            random_seed=args.seed,
            workload_type="synthetic_matrix",
            workload_params=workload_params,
            notes=args.notes,
        )

    runner = BenchmarkRunner()
    record = runner.run(config)

    print(f"Experiment {record.experiment_id} finished.")
    print(f"Status   : {record.status.value}")
    print(f"Decision : {record.decision.value}")
    print(f"Duration : {record.duration_seconds} s")
    print(f"Artifacts: {runner.registry.get_experiment_dir(record.experiment_id)}")
    if record.failure_reason:
        print(f"Failure  : {record.failure_reason}")


if __name__ == "__main__":
    main()
