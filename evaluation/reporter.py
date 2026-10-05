"""Experiment Report Generator for Phase 0 Research Foundation.

Produces unified, scientific, reproducible markdown and JSON reports for individual
experiments following the strict scientific standards of Phase 0.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from runtime.config.schema import ExperimentRecord, ExperimentStatus


class ExperimentReporter:
    """Generates standardized experiment reports in Markdown format."""

    @staticmethod
    def generate_markdown(record: ExperimentRecord) -> str:
        """Construct a comprehensive markdown report for an experiment record."""
        status_badge = record.status.value
        decision_badge = record.decision.value

        lines = [
            f"# Experiment Report: {record.experiment_id}",
            "",
            f"**Experiment Name:** {record.experiment_name}  ",
            f"**Status:** `{status_badge}`  ",
            f"**Scientific Decision:** `{decision_badge}`  ",
            f"**Timestamp (Created):** {record.timestamp}  ",
            f"**Start Time:** {record.start_time or 'N/A'}  ",
            f"**End Time:** {record.end_time or 'N/A'}  ",
            f"**Duration:** {f'{record.duration_seconds:.4f} s' if record.duration_seconds is not None else 'N/A'}  ",
            "",
            "---",
            "",
            "## 1. Scientific Context",
            "",
            f"- **Hypothesis:** {record.hypothesis}",
            f"- **Objective:** {record.objective}",
            f"- **Model Identifier:** `{record.model_identifier}`",
            f"- **Model Revision:** `{record.model_revision}`",
            f"- **Random Seed:** `{record.random_seed}`",
            "",
            "---",
            "",
            "## 2. Environment & Traceability",
            "",
            f"- **Git Commit:** `{record.git_commit}` (Dirty: `{record.git_is_dirty}`)",
            f"- **Git Branch:** `{record.git_branch}`",
            f"- **Hardware Fingerprint:** `{record.hardware_fingerprint}`",
            f"- **Software Fingerprint:** `{record.software_fingerprint}`",
            f"- **OS:** {record.software_environment.get('os_distro', 'N/A')}",
            f"- **Kernel:** {record.software_environment.get('kernel_version', 'N/A')}",
            f"- **Python Version:** {record.software_environment.get('python_version', 'N/A')}",
            "",
            "### Hardware Profile Summary",
            "",
        ]

        hw = record.hardware_profile
        cpu_model = hw.get("cpu_model", {}).get("value", "N/A")
        phys_cores = hw.get("cpu_cores_physical", {}).get("value", "N/A")
        log_cores = hw.get("cpu_cores_logical", {}).get("value", "N/A")
        ram_bytes = hw.get("ram_total_bytes", {}).get("value")
        ram_gb = f"{ram_bytes / (1024**3):.2f} GB" if ram_bytes else "N/A"
        gpu_name = hw.get("gpu_name", {}).get("value") or "None"
        gpu_status = hw.get("gpu_name", {}).get("status", "unavailable")
        gpu_reason = hw.get("gpu_name", {}).get("reason", "")

        lines.extend([
            f"- **CPU Model:** {cpu_model}",
            f"- **CPU Cores:** {phys_cores} physical / {log_cores} logical",
            f"- **RAM Total:** {ram_gb}",
            f"- **GPU Device:** {gpu_name} (Status: `{gpu_status}`, Reason: {gpu_reason or 'None'})",
            f"- **CUDA Version:** {hw.get('cuda_version', {}).get('value') or 'N/A'} (Status: `{hw.get('cuda_version', {}).get('status', 'unavailable')}`)",
            f"- **PyTorch Version:** {hw.get('pytorch_version', {}).get('value') or 'N/A'} (Status: `{hw.get('pytorch_version', {}).get('status', 'unavailable')}`)",
            "",
            "---",
            "",
            "## 3. Experiment Configuration",
            "",
            "```json",
            json.dumps(record.configuration, indent=2),
            "```",
            "",
            "---",
            "",
            "## 4. Resource & Execution Telemetry",
            "",
        ])

        metrics = record.metrics
        time_m = metrics.get("time", {})
        cpu_m = metrics.get("cpu", {})
        mem_m = metrics.get("memory", {})
        gpu_m = metrics.get("gpu", {})
        disk_m = metrics.get("disk", {})
        work_m = metrics.get("workload_metrics", {})

        lines.extend([
            "### Timing Telemetry",
            f"- **Total Wall-Clock Time:** {time_m.get('wall_clock_seconds', 'N/A')} s",
            f"- **Measurement Harness Overhead:** {time_m.get('overhead_seconds', 'N/A')} s",
            "",
            "### Compute & Memory Telemetry",
            f"- **CPU Mean Utilization:** {cpu_m.get('cpu_percent_mean', 'N/A')}%",
            f"- **CPU Peak Utilization:** {cpu_m.get('cpu_percent_peak', 'N/A')}%",
            f"- **User CPU Time:** {cpu_m.get('user_time_seconds', 'N/A')} s",
            f"- **System CPU Time:** {cpu_m.get('system_time_seconds', 'N/A')} s",
            f"- **Start RSS Memory:** {round(mem_m.get('start_rss_bytes', 0) / (1024**2), 2)} MB",
            f"- **Peak RSS Memory:** {round(mem_m.get('peak_rss_bytes', 0) / (1024**2), 2)} MB",
            f"- **End RSS Memory:** {round(mem_m.get('end_rss_bytes', 0) / (1024**2), 2)} MB",
            f"- **Delta RSS Memory:** {round(mem_m.get('delta_rss_bytes', 0) / (1024**2), 2)} MB",
            "",
            "### Accelerator (GPU/VRAM) Telemetry",
            f"- **Status:** `{gpu_m.get('status', 'unavailable')}`",
            f"- **Reason:** {gpu_m.get('reason', 'N/A')}",
            f"- **Peak VRAM:** {gpu_m.get('peak_vram_bytes', 'N/A')}",
            "",
            "### Storage & Artifacts Footprint",
            f"- **Artifacts Size:** {disk_m.get('artifacts_bytes', 0)} bytes",
            f"- **Disk Free Delta:** {disk_m.get('delta_free_bytes', 0)} bytes",
            "",
            "### Workload Specific Outputs",
            f"- **Iterations Completed:** {work_m.get('iterations_completed', 'N/A')}",
            f"- **Output Digest (SHA-256):** `{work_m.get('output_sha256', 'N/A')}`",
            "",
            "---",
            "",
            "## 5. Artifacts & Outputs",
            "",
        ])

        if record.artifacts:
            for art_name, art_meta in record.artifacts.items():
                if isinstance(art_meta, dict):
                    path = art_meta.get("path", "")
                    size = art_meta.get("bytes", 0)
                    sha = art_meta.get("sha256", "N/A")
                    lines.append(f"- **{art_name}:** `{path}` ({size} bytes, SHA-256: `{sha}`)")
                else:
                    lines.append(f"- **{art_name}:** `{art_meta}`")
        else:
            lines.append("No persistent artifacts recorded.")

        lines.extend([
            "",
            "---",
            "",
            "## 6. Logs & Diagnostics",
            "",
            f"- **Log File:** `{record.logs.get('log_file', 'N/A')}`",
            f"- **Log Lines Count:** {record.logs.get('line_count', 0)}",
            "",
        ])

        if record.status == ExperimentStatus.FAILED:
            lines.extend([
                "---",
                "",
                "## 7. Failure Analysis & Diagnostics",
                "",
                f"**Failure Reason:** {record.failure_reason}",
                "",
                "**Stack Trace:**",
                "```text",
                record.stack_trace or "No stack trace available.",
                "```",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 8. Notes & Conclusions",
            "",
            record.notes or "No additional notes provided.",
            "",
        ])

        return "\n".join(lines)

    @classmethod
    def save_report(cls, record: ExperimentRecord, output_file: Path) -> None:
        """Write report to file."""
        report_md = cls.generate_markdown(record)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_md)
