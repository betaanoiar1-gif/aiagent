"""Validation tests for Experiment Reproducibility and Differential Analysis."""

from runtime.config.experiment_config import ExperimentConfig
from runtime.runner.reproducibility import ReproducibilityEngine
from runtime.runner.runner import BenchmarkRunner


def test_reproducibility_deterministic_match(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify that reproducing an experiment with identical seed produces bitwise identical output."""
    rec1 = test_runner.run(sample_experiment_config)

    repro_engine = ReproducibilityEngine(registry=test_runner.registry, runner=test_runner)
    rec2, comparison = repro_engine.reproduce(rec1.experiment_id)

    # Identifiers must be unique
    assert rec1.experiment_id != rec2.experiment_id

    # Mathematical outputs must be bitwise identical
    assert comparison.bitwise_identical_output is True
    assert comparison.reproducibility_verdict == "DETERMINISTIC_MATCH"
    assert comparison.configurations_match is True
    assert comparison.seeds_match is True

    # Hashes match
    sha1 = rec1.metrics["workload_metrics"]["output_sha256"]
    sha2 = rec2.metrics["workload_metrics"]["output_sha256"]
    assert sha1 == sha2


def test_reproducibility_detects_seed_divergence(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify that modifying the seed produces divergent output checksums."""
    rec1 = test_runner.run(sample_experiment_config)

    repro_engine = ReproducibilityEngine(registry=test_runner.registry, runner=test_runner)
    # Reproduce with changed seed
    rec2, comparison = repro_engine.reproduce(rec1.experiment_id, custom_seed=999999)

    assert comparison.bitwise_identical_output is False
    assert comparison.seeds_match is False
    assert comparison.reproducibility_verdict == "CONFIG_MISMATCH"
