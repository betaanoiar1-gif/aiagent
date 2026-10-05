"""Reproducibility Engine for Phase 0 Research Foundation.

Implements the mechanism to load a previously executed experiment, replicate its
configuration and random seed, re-execute the experiment, and perform rigorous
comparative validation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from evaluation.comparison import ComparisonResult, ExperimentComparator
from runtime.config.experiment_config import ExperimentConfig
from runtime.config.runtime_config import RuntimeConfig
from runtime.config.schema import ExperimentRecord
from runtime.registry.registry import ExperimentRegistry
from runtime.runner.runner import BenchmarkRunner


class ReproducibilityEngine:
    """Automates replication and validation of experiments."""

    def __init__(
        self,
        registry: Optional[ExperimentRegistry] = None,
        runner: Optional[BenchmarkRunner] = None,
    ) -> None:
        self.registry = registry or ExperimentRegistry()
        self.runner = runner or BenchmarkRunner(registry=self.registry)

    def reproduce(
        self,
        target_experiment_id: str,
        custom_seed: Optional[int] = None,
    ) -> Tuple[ExperimentRecord, ComparisonResult]:
        """Load experiment config, re-execute, and compare results."""
        # 1. Fetch original record
        orig_record = self.registry.get(target_experiment_id)
        if orig_record is None:
            raise ValueError(f"Experiment ID '{target_experiment_id}' does not exist in registry.")

        # 2. Reconstruct experiment configuration
        exp_dir = self.registry.get_experiment_dir(target_experiment_id)
        config_path = exp_dir / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing config.json in experiment directory: {exp_dir}")

        config = ExperimentConfig.from_json_file(config_path)

        # Clear experiment_id so a new unique ID is allocated for the replica
        config.experiment_id = None
        if custom_seed is not None:
            config.random_seed = custom_seed

        # Annotate notes to indicate replication
        config.notes = (
            f"Reproduction run of experiment '{target_experiment_id}'. "
            f"Original commit: {orig_record.git_commit}. "
            f"{config.notes}"
        ).strip()

        # Reconstruct runtime config if available
        rc_dict = orig_record.runtime_configuration
        rc = RuntimeConfig.from_dict(rc_dict) if rc_dict else RuntimeConfig()

        # 3. Execute replica
        replica_record = self.runner.run(config, runtime_config=rc)

        # 4. Compare original vs replica
        comparison = ExperimentComparator.compare(orig_record, replica_record)

        # 5. Save comparison report inside the replica directory and research/reports
        comparison_md = ExperimentComparator.generate_markdown_report(comparison)
        replica_dir = self.registry.get_experiment_dir(replica_record.experiment_id)
        with open(replica_dir / "reproducibility_report.md", "w", encoding="utf-8") as f:
            f.write(comparison_md)

        # Also write to research/reports/
        reports_dir = Path("research/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = (
            reports_dir
            / f"comparison_{orig_record.experiment_id}_vs_{replica_record.experiment_id}.md"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(comparison_md)

        return replica_record, comparison
