"""Validation tests for Comparison reports and Markdown report generation."""

from evaluation.comparison import ExperimentComparator
from evaluation.reporter import ExperimentReporter
from runtime.config.experiment_config import ExperimentConfig
from runtime.runner.runner import BenchmarkRunner


def test_markdown_report_structure(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify generated report.md contains all required sections and data points."""
    record = test_runner.run(sample_experiment_config)
    md = ExperimentReporter.generate_markdown(record)

    # Core sections check
    assert f"# Experiment Report: {record.experiment_id}" in md
    assert "## 1. Scientific Context" in md
    assert "## 2. Environment & Traceability" in md
    assert "## 3. Experiment Configuration" in md
    assert "## 4. Resource & Execution Telemetry" in md
    assert "## 5. Artifacts & Outputs" in md
    assert "## 6. Logs & Diagnostics" in md
    assert "Hardware Fingerprint" in md
    assert "Total Wall-Clock Time" in md
    assert record.hypothesis in md


def test_comparison_report_markdown(test_runner: BenchmarkRunner, sample_experiment_config: ExperimentConfig):
    """Verify generated comparison markdown report includes parity matrix and telemetry differences."""
    rec1 = test_runner.run(sample_experiment_config)
    sample_experiment_config.random_seed = 456
    rec2 = test_runner.run(sample_experiment_config)

    comp = ExperimentComparator.compare(rec1, rec2)
    comp_md = ExperimentComparator.generate_markdown_report(comp)

    assert f"# Experiment Comparison: `{rec1.experiment_id}` vs `{rec2.experiment_id}`" in comp_md
    assert "## 1. Parity Matrix" in comp_md
    assert "## 2. Resource Variance & Natural Jitter" in comp_md
    assert "## 3. Findings & Scientific Analysis" in comp_md
