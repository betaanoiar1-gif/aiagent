"""Validation tests for Artifact Management and Isolation."""

from pathlib import Path
from runtime.config.experiment_config import ExperimentConfig
from runtime.runner.runner import BenchmarkRunner


def test_artifact_isolation(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify separate experiments write strictly to their own independent directories."""
    rec1 = test_runner.run(sample_experiment_config)
    dir1 = test_runner.registry.get_experiment_dir(rec1.experiment_id)

    # Change seed and run second
    sample_experiment_config.random_seed = 999
    sample_experiment_config.experiment_id = None
    rec2 = test_runner.run(sample_experiment_config)
    dir2 = test_runner.registry.get_experiment_dir(rec2.experiment_id)

    assert dir1 != dir2
    assert dir1.exists()
    assert dir2.exists()

    # Check that artifact SHA digests in rec1 point only to dir1 files
    for art_path, art_info in rec1.artifacts.items():
        assert (dir1 / art_path).exists()
        assert not (dir1 / art_path).is_symlink()


def test_artifact_checksum_integrity(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify artifact catalog hashes accurately match file content on disk."""
    import hashlib

    record = test_runner.run(sample_experiment_config)
    exp_dir = test_runner.registry.get_experiment_dir(record.experiment_id)

    for rel_path, meta in record.artifacts.items():
        disk_file = exp_dir / rel_path
        assert disk_file.exists()
        with open(disk_file, "rb") as f:
            computed_sha = hashlib.sha256(f.read()).hexdigest()
        assert meta["sha256"] == computed_sha
