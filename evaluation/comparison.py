"""Experiment Comparison and Reproducibility Analysis Engine for Phase 0.

Compares two experiment records to evaluate determinism, configuration parity,
output identity, and resource variances, isolating natural runtime non-determinism.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.config.schema import ExperimentRecord


@dataclass
class MetricDiff:
    """Numerical metric comparison."""
    val1: Any
    val2: Any
    delta: Optional[float]
    pct_delta: Optional[float]


@dataclass
class ComparisonResult:
    """Outcome of comparing two experiments."""
    exp1_id: str
    exp2_id: str
    seed1: int
    seed2: int
    hypotheses_match: bool
    configurations_match: bool
    seeds_match: bool
    hardware_fingerprints_match: bool
    software_fingerprints_match: bool
    output_checksums_match: bool
    bitwise_identical_output: bool

    # Metric diffs
    duration_diff: MetricDiff
    cpu_mean_diff: MetricDiff
    peak_rss_diff: MetricDiff

    # Analysis
    natural_jitter_observed: bool
    reproducibility_verdict: str  # "DETERMINISTIC_MATCH", "DIVERGENT", "CONFIG_MISMATCH"
    analysis_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exp1_id": self.exp1_id,
            "exp2_id": self.exp2_id,
            "seed1": self.seed1,
            "seed2": self.seed2,
            "hypotheses_match": self.hypotheses_match,
            "configurations_match": self.configurations_match,
            "seeds_match": self.seeds_match,
            "hardware_fingerprints_match": self.hardware_fingerprints_match,
            "software_fingerprints_match": self.software_fingerprints_match,
            "output_checksums_match": self.output_checksums_match,
            "bitwise_identical_output": self.bitwise_identical_output,
            "duration_diff": asdict(self.duration_diff),
            "cpu_mean_diff": asdict(self.cpu_mean_diff),
            "peak_rss_diff": asdict(self.peak_rss_diff),
            "natural_jitter_observed": self.natural_jitter_observed,
            "reproducibility_verdict": self.reproducibility_verdict,
            "analysis_notes": self.analysis_notes,
        }


class ExperimentComparator:
    """Compares two experiment records."""

    @classmethod
    def compare(cls, exp1: ExperimentRecord, exp2: ExperimentRecord) -> ComparisonResult:
        """Compare exp1 and exp2 in detail."""
        hypotheses_match = (exp1.hypothesis == exp2.hypothesis)
        # Compare core scientific configuration, excluding notes and experiment_id annotations
        cfg1_core = {k: v for k, v in exp1.configuration.items() if k not in {"notes", "experiment_id"}}
        cfg2_core = {k: v for k, v in exp2.configuration.items() if k not in {"notes", "experiment_id"}}
        configurations_match = (cfg1_core == cfg2_core)
        seeds_match = (exp1.random_seed == exp2.random_seed)
        hw_match = (exp1.hardware_fingerprint == exp2.hardware_fingerprint)
        sw_match = (exp1.software_fingerprint == exp2.software_fingerprint)

        # Output checksum comparison
        out1_sha = exp1.metrics.get("workload_metrics", {}).get("output_sha256")
        out2_sha = exp2.metrics.get("workload_metrics", {}).get("output_sha256")
        out_match = bool(out1_sha and out2_sha and out1_sha == out2_sha)
        bitwise_identical = out_match

        # Duration comparison
        dur1 = exp1.duration_seconds or 0.0
        dur2 = exp2.duration_seconds or 0.0
        dur_delta = round(dur2 - dur1, 6)
        dur_pct = round((dur_delta / dur1 * 100.0), 2) if dur1 > 0 else 0.0
        dur_diff = MetricDiff(val1=dur1, val2=dur2, delta=dur_delta, pct_delta=dur_pct)

        # CPU mean comparison
        cpu1 = exp1.metrics.get("cpu", {}).get("cpu_percent_mean", 0.0)
        cpu2 = exp2.metrics.get("cpu", {}).get("cpu_percent_mean", 0.0)
        cpu_delta = round(cpu2 - cpu1, 2)
        cpu_pct = round((cpu_delta / cpu1 * 100.0), 2) if cpu1 > 0 else 0.0
        cpu_diff = MetricDiff(val1=cpu1, val2=cpu2, delta=cpu_delta, pct_delta=cpu_pct)

        # Peak RSS comparison
        rss1 = exp1.metrics.get("memory", {}).get("peak_rss_bytes", 0)
        rss2 = exp2.metrics.get("memory", {}).get("peak_rss_bytes", 0)
        rss_delta = rss2 - rss1
        rss_pct = round((rss_delta / rss1 * 100.0), 2) if rss1 > 0 else 0.0
        rss_diff = MetricDiff(val1=rss1, val2=rss2, delta=rss_delta, pct_delta=rss_pct)

        notes = []
        if not seeds_match:
            notes.append("Random seeds differ; deterministic identical outputs not expected.")
        if not configurations_match:
            notes.append("Configurations differ between experiments.")

        natural_jitter = False
        if out_match and (abs(dur_delta) > 1e-6 or rss_delta != 0 or cpu_delta != 0):
            natural_jitter = True
            notes.append(
                f"Workload output hashes are bitwise identical ({out1_sha}). "
                f"Observed natural wall-clock variance of {dur_delta:+.4f}s ({dur_pct:+.2f}%) "
                f"and peak memory delta of {rss_delta / (1024**2):+.2f}MB due to OS thread scheduling and paging."
            )

        if not out_match and seeds_match and configurations_match:
            reproducibility_verdict = "DIVERGENT"
            notes.append("ALERT: Identical configurations and seeds produced different outputs!")
        elif out_match and seeds_match and configurations_match:
            reproducibility_verdict = "DETERMINISTIC_MATCH"
            notes.append("Scientific reproducibility confirmed: mathematical outputs are bitwise identical.")
        else:
            reproducibility_verdict = "CONFIG_MISMATCH"

        return ComparisonResult(
            exp1_id=exp1.experiment_id,
            exp2_id=exp2.experiment_id,
            seed1=exp1.random_seed,
            seed2=exp2.random_seed,
            hypotheses_match=hypotheses_match,
            configurations_match=configurations_match,
            seeds_match=seeds_match,
            hardware_fingerprints_match=hw_match,
            software_fingerprints_match=sw_match,
            output_checksums_match=out_match,
            bitwise_identical_output=bitwise_identical,
            duration_diff=dur_diff,
            cpu_mean_diff=cpu_diff,
            peak_rss_diff=rss_diff,
            natural_jitter_observed=natural_jitter,
            reproducibility_verdict=reproducibility_verdict,
            analysis_notes=notes,
        )

    @classmethod
    def generate_markdown_report(cls, comp: ComparisonResult) -> str:
        """Produce markdown comparison report."""
        lines = [
            f"# Experiment Comparison: `{comp.exp1_id}` vs `{comp.exp2_id}`",
            "",
            f"**Reproducibility Verdict:** `{comp.reproducibility_verdict}`  ",
            f"**Bitwise Identical Output:** `{comp.bitwise_identical_output}`  ",
            f"**Hardware Match:** `{comp.hardware_fingerprints_match}`  ",
            f"**Software Match:** `{comp.software_fingerprints_match}`  ",
            "",
            "---",
            "",
            "## 1. Parity Matrix",
            "",
            "| Dimension | Experiment 1 (`" + comp.exp1_id + "`) | Experiment 2 (`" + comp.exp2_id + "`) | Match? |",
            "| :--- | :--- | :--- | :--- |",
            f"| Random Seed | `{comp.seed1}` | `{comp.seed2}` | `{comp.seeds_match}` |",
            f"| Configuration | - | - | `{comp.configurations_match}` |",
            f"| Hardware Fingerprint | - | - | `{comp.hardware_fingerprints_match}` |",
            f"| Software Fingerprint | - | - | `{comp.software_fingerprints_match}` |",
            f"| Output Checksum Match | - | - | `{comp.output_checksums_match}` |",
            "",
            "---",
            "",
            "## 2. Resource Variance & Natural Jitter",
            "",
            "| Metric | " + comp.exp1_id + " | " + comp.exp2_id + " | Delta | % Delta |",
            "| :--- | :--- | :--- | :--- | :--- |",
            f"| Wall-Clock Time (s) | {comp.duration_diff.val1:.4f} | {comp.duration_diff.val2:.4f} | {comp.duration_diff.delta:+.4f} | {comp.duration_diff.pct_delta:+.2f}% |",
            f"| CPU Mean (%) | {comp.cpu_mean_diff.val1} | {comp.cpu_mean_diff.val2} | {comp.cpu_mean_diff.delta:+} | {comp.cpu_mean_diff.pct_delta:+}% |",
            f"| Peak RSS (MB) | {comp.peak_rss_diff.val1 / (1024**2):.2f} | {comp.peak_rss_diff.val2 / (1024**2):.2f} | {comp.peak_rss_diff.delta / (1024**2):+.2f} | {comp.peak_rss_diff.pct_delta:+.2f}% |",
            "",
            "---",
            "",
            "## 3. Findings & Scientific Analysis",
            "",
        ]

        for note in comp.analysis_notes:
            lines.append(f"- {note}")

        lines.append("")
        return "\n".join(lines)
