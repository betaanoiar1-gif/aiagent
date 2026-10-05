"""Validation tests for Experiment Registry indexing and persistence."""

from runtime.config.schema import ExperimentRecord, ExperimentStatus, ResearchDecision
from runtime.registry.registry import ExperimentRegistry


def test_experiment_id_allocation(test_registry: ExperimentRegistry):
    """Verify sequential, collision-free allocation of experiment IDs."""
    id1 = test_registry.allocate_experiment_id()
    id2 = test_registry.allocate_experiment_id()
    id3 = test_registry.allocate_experiment_id()

    assert id1 == "EXP-000001"
    assert id2 == "EXP-000002"
    assert id3 == "EXP-000003"
    assert len({id1, id2, id3}) == 3


def test_registry_registration_and_lookup(test_registry: ExperimentRegistry):
    """Verify registering an experiment record and retrieving it by ID."""
    exp_id = test_registry.allocate_experiment_id()
    record = ExperimentRecord(
        experiment_id=exp_id,
        experiment_name="reg-test",
        hypothesis="H_lookup",
        objective="O_lookup",
        timestamp="2026-10-05T00:00:00Z",
        status=ExperimentStatus.CREATED,
        decision=ResearchDecision.PENDING,
        random_seed=777,
    )

    test_registry.register(record)

    assert test_registry.exists(exp_id)
    retrieved = test_registry.get(exp_id)
    assert retrieved is not None
    assert retrieved.experiment_id == exp_id
    assert retrieved.experiment_name == "reg-test"
    assert retrieved.random_seed == 777
    assert retrieved.status == ExperimentStatus.CREATED


def test_registry_lookup_nonexistent(test_registry: ExperimentRegistry):
    """Verify querying non-existent ID gracefully returns None."""
    assert not test_registry.exists("EXP-999999")
    assert test_registry.get("EXP-999999") is None


def test_registry_listing_and_filtering(test_registry: ExperimentRegistry):
    """Verify registry listing with status and query filters."""
    for i, st in enumerate([ExperimentStatus.COMPLETED, ExperimentStatus.FAILED, ExperimentStatus.COMPLETED]):
        exp_id = test_registry.allocate_experiment_id()
        rec = ExperimentRecord(
            experiment_id=exp_id,
            experiment_name=f"exp-filter-{i}",
            hypothesis=f"Hypothesis {i}",
            objective="Testing filters",
            timestamp="2026-10-05T00:00:00Z",
            status=st,
        )
        test_registry.register(rec)

    completed = test_registry.list(status=ExperimentStatus.COMPLETED)
    assert len(completed) == 2
    failed = test_registry.list(status=ExperimentStatus.FAILED)
    assert len(failed) == 1

    queried = test_registry.list(query="exp-filter-1")
    assert len(queried) == 1
    assert queried[0]["experiment_name"] == "exp-filter-1"
