"""Validation tests for Baseline Generation Engine and physical requirement checks."""

import pytest
from engines.baseline_engine import (
    BaselineGenerationEngine,
    EnvironmentHardwarePrerequisiteError,
)


def test_baseline_engine_hardware_audit_failure():
    """Verify engine detects missing physical accelerator and raises explicit error."""
    engine = BaselineGenerationEngine()
    engine.initialize({})

    # Attempt to execute without GPU
    with pytest.raises(EnvironmentHardwarePrerequisiteError) as exc_info:
        engine.execute(
            workload_params={
                "model_identifier": "runwayml/stable-diffusion-v1-5",
                "prompt_id": "I01",
            },
            random_seed=101,
            output_dir="/tmp/test_baseline_out",
        )

    err = str(exc_info.value)
    assert "EnvironmentHardwarePrerequisiteError" in err
    assert "Missing physical GPU" in err
    assert "CUDA compiler/runtime unavailable" in err
    assert "CPU-only generation is prohibited" in err

    engine.teardown()
