"""Validation tests for Benchmark Runner end-to-end execution and artifact emission."""

import json
from pathlib import Path
from runtime.config.experiment_config import ExperimentConfig
from runtime.config.schema import ExperimentStatus
from runtime.runner.runner import BenchmarkRunner


def test_benchmark_runner_full_pipeline(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify BenchmarkRunner creates all required artifacts and directory layout."""
    record = test_runner.run(sample_experiment_config)
    exp_dir = test_runner.registry.get_experiment_dir(record.experiment_id)

    # 1. Root experiment artifacts
    assert (exp_dir / "config.json").exists()
    assert (exp_dir / "metadata.json").exists()
    assert (exp_dir / "metrics.json").exists()
    assert (exp_dir / "report.md").exists()

    # 2. Environment subdirectory
    assert (exp_dir / "environment" / "hardware.json").exists()
    assert (exp_dir / "environment" / "software.json").exists()

    # 3. Logs subdirectory
    assert (exp_dir / "logs" / "execution.log").exists()
    with open(exp_dir / "logs" / "execution.log", "r", encoding="utf-8") as f:
        log_content = f.read()
    assert f"=== Initializing Experiment: {record.experiment_id}" in log_content
    assert "Workload completed successfully" in log_content

    # 4. Outputs subdirectory
    assert (exp_dir / "outputs" / "output_manifest.json").exists()
    assert (exp_dir / "outputs" / "synthetic_feature_map.ppm").exists()

    # 5. Metrics integrity
    with open(exp_dir / "metrics.json", "r", encoding="utf-8") as f:
        metrics_data = json.load(f)
    assert "time" in metrics_data
    assert "cpu" in metrics_data
    assert "memory" in metrics_data
    assert "gpu" in metrics_data
    assert "disk" in metrics_data
    assert metrics_data["workload_metrics"]["iterations_completed"] == 100
