"""Validation tests for Experiment Lifecycle state transitions."""

from runtime.config.experiment_config import ExperimentConfig
from runtime.config.schema import ExperimentStatus, ResearchDecision
from runtime.runner.runner import BenchmarkRunner


def test_successful_lifecycle(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify CREATED -> RUNNING -> COMPLETED state transitions and timestamps."""
    record = test_runner.run(sample_experiment_config)

    assert record.status == ExperimentStatus.COMPLETED
    assert record.decision == ResearchDecision.PASS
    assert record.start_time is not None
    assert record.end_time is not None
    assert record.duration_seconds is not None
    assert record.duration_seconds > 0.0
    assert record.failure_reason is None
    assert record.stack_trace is None


def test_failed_lifecycle(test_runner: BenchmarkRunner):
    """Verify CREATED -> RUNNING -> FAILED state transitions and error recording."""
    fail_config = ExperimentConfig(
        experiment_name="fail-test",
        hypothesis="Exception triggers proper FAILED state transition.",
        objective="Verify fault handling.",
        model_identifier="test-model",
        model_revision="v0",
        random_seed=123,
        workload_params={
            "simulate_failure": True,
            "failure_step": 1,
            "failure_message": "Forced test failure in runner",
        },
    )

    record = test_runner.run(fail_config)

    assert record.status == ExperimentStatus.FAILED
    assert record.decision == ResearchDecision.FAIL
    assert record.start_time is not None
    assert record.end_time is not None
    assert record.duration_seconds is not None
    assert "Forced test failure in runner" in (record.failure_reason or "")
    assert record.stack_trace is not None
    assert "Traceback" in record.stack_trace
