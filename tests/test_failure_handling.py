"""Validation tests for Failure Handling and Data Preservation."""

from runtime.config.experiment_config import ExperimentConfig
from runtime.config.schema import ExperimentStatus, ResearchDecision
from runtime.runner.runner import BenchmarkRunner


def test_failure_preserves_all_metadata_and_artifacts(test_runner: BenchmarkRunner):
    """Verify that failure does NOT discard metadata, environment, logs, or metrics."""
    fail_cfg = ExperimentConfig(
        experiment_name="crash-resilience-test",
        hypothesis="H_failure_persistence",
        objective="O_failure_persistence",
        model_identifier="failing-model",
        model_revision="v0",
        random_seed=404,
        workload_params={
            "simulate_failure": True,
            "failure_step": 13,
            "failure_message": "CRITICAL_SIMULATED_WORKLOAD_ABORT",
        },
    )

    record = test_runner.run(fail_cfg)
    exp_dir = test_runner.registry.get_experiment_dir(record.experiment_id)

    # Status must be FAILED
    assert record.status == ExperimentStatus.FAILED
    assert record.decision == ResearchDecision.FAIL
    assert record.failure_reason is not None
    assert "CRITICAL_SIMULATED_WORKLOAD_ABORT" in record.failure_reason
    assert record.stack_trace is not None

    # Crucial rule: All data files must exist and be intact
    assert (exp_dir / "config.json").exists()
    assert (exp_dir / "metadata.json").exists()
    assert (exp_dir / "metrics.json").exists()
    assert (exp_dir / "report.md").exists()
    assert (exp_dir / "logs" / "execution.log").exists()
    assert (exp_dir / "environment" / "hardware.json").exists()
    assert (exp_dir / "environment" / "software.json").exists()

    # Log file should document the failure
    with open(exp_dir / "logs" / "execution.log", "r", encoding="utf-8") as f:
        log_text = f.read()
    assert "Experiment FAILED: EngineExecutionFailure: CRITICAL_SIMULATED_WORKLOAD_ABORT" in log_text

    # Registry lookup should retrieve the failed record without error
    retrieved = test_runner.registry.get(record.experiment_id)
    assert retrieved is not None
    assert retrieved.status == ExperimentStatus.FAILED
