"""Shared pytest fixtures for Phase 0 Research Foundation test suite."""

import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from runtime.config.experiment_config import ExperimentConfig
from runtime.config.runtime_config import RuntimeConfig
from runtime.registry.registry import ExperimentRegistry
from runtime.runner.runner import BenchmarkRunner


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory cleaned up after test completion."""
    tmp = tempfile.mkdtemp(prefix="research_test_")
    tmp_path = Path(tmp)
    try:
        yield tmp_path
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def test_registry(temp_dir: Path) -> ExperimentRegistry:
    """Provide an isolated ExperimentRegistry in temporary storage."""
    exp_dir = temp_dir / "experiments"
    return ExperimentRegistry(base_dir=str(exp_dir))


@pytest.fixture
def test_runner(test_registry: ExperimentRegistry) -> BenchmarkRunner:
    """Provide an isolated BenchmarkRunner."""
    return BenchmarkRunner(registry=test_registry)


@pytest.fixture
def sample_experiment_config() -> ExperimentConfig:
    """Provide a valid ExperimentConfig for testing."""
    return ExperimentConfig(
        experiment_name="unit-test-workload",
        hypothesis="Deterministic PRNG workload produces identical hashes given seed 123.",
        objective="Validate test runner pipeline and metrics capture.",
        model_identifier="test-model-v0",
        model_revision="v0.1",
        random_seed=123,
        workload_type="synthetic_matrix",
        workload_params={"iterations": 100, "matrix_size": 16},
        tags=["unit_test", "phase0"],
        notes="Automated unit test execution.",
    )
