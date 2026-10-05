"""Validation tests for the Configuration Separation and Schema."""

import json
from pathlib import Path
import pytest

from runtime.config.experiment_config import ExperimentConfig
from runtime.config.runtime_config import RuntimeConfig
from runtime.config.schema import ExperimentRecord, ExperimentStatus, ResearchDecision


def test_experiment_config_validation():
    """Verify validation of required experiment configuration fields."""
    # Valid config
    cfg = ExperimentConfig(
        experiment_name="valid-exp",
        hypothesis="H1",
        objective="O1",
        model_identifier="M1",
        model_revision="R1",
        random_seed=42,
    )
    assert cfg.random_seed == 42
    assert cfg.workload_type == "synthetic_matrix"

    # Missing required field should raise ValueError
    invalid_data = {
        "experiment_name": "missing-seed",
        "hypothesis": "H1",
        "objective": "O1",
        # random_seed missing!
    }
    with pytest.raises(ValueError) as exc_info:
        ExperimentConfig.from_dict(invalid_data)
    assert "Missing required ExperimentConfig fields" in str(exc_info.value)


def test_config_serialization(temp_dir: Path):
    """Verify JSON save and load round-trip fidelity."""
    cfg = ExperimentConfig(
        experiment_name="serialize-test",
        hypothesis="H_roundtrip",
        objective="O_roundtrip",
        model_identifier="model-x",
        model_revision="v2",
        random_seed=999,
        workload_params={"size": 128, "flag": True},
    )

    path = temp_dir / "cfg.json"
    cfg.save_json(path)
    assert path.exists()

    loaded = ExperimentConfig.from_json_file(path)
    assert loaded.experiment_name == cfg.experiment_name
    assert loaded.random_seed == cfg.random_seed
    assert loaded.workload_params == cfg.workload_params


def test_runtime_config_separation():
    """Verify runtime configuration is decoupled from experiment hypothesis."""
    rc = RuntimeConfig(
        output_dir="/custom/dir",
        timeout_seconds=60.0,
        sample_interval_ms=25,
        log_level="DEBUG",
    )
    assert rc.timeout_seconds == 60.0
    d = rc.to_dict()
    assert d["sample_interval_ms"] == 25
    assert "hypothesis" not in d  # Pure runtime settings
