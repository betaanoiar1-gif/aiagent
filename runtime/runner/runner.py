"""Benchmark Runner for Phase 0 Research Foundation.

Implements the formal scientific experiment execution lifecycle:
CREATED -> RUNNING -> COMPLETED (or FAILED).
Coordinates configuration loading, hardware & software profiling, resource
monitoring, workload execution, artifact storage, failure handling, and report generation.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from engines.base import BaseEngine
from engines.mock_engine import DeterministicSyntheticEngine
from evaluation.reporter import ExperimentReporter
from models.base import BaseModel
from models.mock_model import SyntheticBenchmarkModel
from runtime.config.experiment_config import ExperimentConfig
from runtime.config.runtime_config import RuntimeConfig
from runtime.config.schema import (
    ExperimentRecord,
    ExperimentStatus,
    ResearchDecision,
)
from runtime.measurement.monitor import ResourceMonitor
from runtime.profiler.hardware import HardwareProfiler
from runtime.profiler.software import SoftwareProfiler
from runtime.registry.registry import ExperimentRegistry


class BenchmarkRunner:
    """Orchestrates scientific experiment execution and lifecycle management."""

    def __init__(
        self,
        registry: Optional[ExperimentRegistry] = None,
        hardware_profiler: Optional[HardwareProfiler] = None,
        software_profiler: Optional[SoftwareProfiler] = None,
    ) -> None:
        self.registry = registry or ExperimentRegistry()
        self.hw_profiler = hardware_profiler or HardwareProfiler()
        self.sw_profiler = software_profiler or SoftwareProfiler()

    def run(
        self,
        experiment_config: ExperimentConfig,
        runtime_config: Optional[RuntimeConfig] = None,
        engine: Optional[BaseEngine] = None,
        model: Optional[BaseModel] = None,
    ) -> ExperimentRecord:
        """Execute the complete experiment lifecycle."""
        rc = runtime_config or RuntimeConfig()

        # Step 1: Allocate unique experiment ID and create directory structure
        if experiment_config.experiment_id:
            exp_id = experiment_config.experiment_id
        else:
            exp_id = self.registry.allocate_experiment_id()

        exp_dir = self.registry.get_experiment_dir(exp_id)
        logs_dir = exp_dir / "logs"
        outputs_dir = exp_dir / "outputs"
        env_dir = exp_dir / "environment"

        for d in [exp_dir, logs_dir, outputs_dir, env_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Step 2: Configure experiment logger
        log_file = logs_dir / "execution.log"
        logger = self._setup_logger(exp_id, log_file, rc.log_level)
        logger.info(f"=== Initializing Experiment: {exp_id} ({experiment_config.experiment_name}) ===")
        logger.info(f"Hypothesis: {experiment_config.hypothesis}")
        logger.info(f"Objective: {experiment_config.objective}")

        # Step 3: Record environment (Hardware & Software)
        logger.info("Profiling hardware and software environment...")
        hw_profile = self.hw_profiler.profile()
        sw_profile = self.sw_profiler.profile()

        # Persist environment artifacts
        hw_file = env_dir / "hardware.json"
        with open(hw_file, "w", encoding="utf-8") as f:
            f.write(hw_profile.to_json(indent=2))

        sw_file = env_dir / "software.json"
        with open(sw_file, "w", encoding="utf-8") as f:
            f.write(sw_profile.to_json(indent=2))

        # Save config.json
        cfg_file = exp_dir / "config.json"
        experiment_config.save_json(cfg_file)

        # Step 4: Create ExperimentRecord with status CREATED
        created_timestamp = datetime.now(timezone.utc).isoformat()
        record = ExperimentRecord(
            experiment_id=exp_id,
            experiment_name=experiment_config.experiment_name,
            hypothesis=experiment_config.hypothesis,
            objective=experiment_config.objective,
            timestamp=created_timestamp,
            status=ExperimentStatus.CREATED,
            git_commit=sw_profile.git_state.commit,
            git_branch=sw_profile.git_state.branch,
            git_is_dirty=sw_profile.git_state.is_dirty,
            hardware_fingerprint=hw_profile.hardware_fingerprint,
            software_fingerprint=sw_profile.software_fingerprint,
            software_environment=sw_profile.to_dict(),
            hardware_profile=hw_profile.to_dict(),
            model_identifier=experiment_config.model_identifier,
            model_revision=experiment_config.model_revision,
            random_seed=experiment_config.random_seed,
            input_reference=experiment_config.input_reference,
            output_reference=experiment_config.output_reference,
            configuration=experiment_config.to_dict(),
            runtime_configuration=rc.to_dict(),
            notes=experiment_config.notes,
        )

        # Persist initial record
        self.registry.register(record)
        logger.info(f"Experiment record registered in status: {record.status.value}")

        # Step 5: Transition to RUNNING
        record.status = ExperimentStatus.RUNNING
        record.start_time = datetime.now(timezone.utc).isoformat()
        self.registry.register(record)
        logger.info(f"Lifecycle transitioned to RUNNING at {record.start_time}")

        # Step 6: Initialize resource monitor and execution components
        active_engine = engine or DeterministicSyntheticEngine()
        active_model = model or SyntheticBenchmarkModel(
            identifier=experiment_config.model_identifier,
            revision=experiment_config.model_revision,
        )

        monitor = ResourceMonitor(
            sample_interval_ms=rc.sample_interval_ms,
            target_path=str(exp_dir),
        )

        t_start = time.perf_counter()
        monitor.start()

        # Step 7: Workload Execution with robust Failure Handling
        try:
            logger.info("Initializing execution engine...")
            active_engine.initialize(rc.to_dict())

            logger.info("Loading model weights / specification...")
            model_telemetry = active_model.load()
            logger.info(f"Model loaded: {model_telemetry}")

            logger.info(
                f"Executing workload '{experiment_config.workload_type}' with seed={experiment_config.random_seed}..."
            )
            workload_res = active_engine.execute(
                workload_params=experiment_config.workload_params,
                random_seed=experiment_config.random_seed,
                output_dir=str(outputs_dir),
            )
            logger.info(f"Workload completed successfully: {workload_res}")

            # Collect metrics
            meas_result = monitor.stop(artifacts_path=str(exp_dir))
            t_end = time.perf_counter()
            duration = t_end - t_start

            meas_result.workload_metrics = workload_res
            meas_result.time.model_load_seconds = model_telemetry.get("load_time_seconds", 0.0)
            meas_result.time.inference_seconds = round(
                duration - meas_result.time.model_load_seconds, 6
            )

            # Finalize COMPLETED state
            record.status = ExperimentStatus.COMPLETED
            record.decision = ResearchDecision.PASS
            record.end_time = datetime.now(timezone.utc).isoformat()
            record.duration_seconds = round(duration, 6)
            record.metrics = meas_result.to_dict()

            logger.info(
                f"Experiment COMPLETED in {record.duration_seconds:.4f}s with decision PASS."
            )

        except Exception as exc:
            # Lifecycle Failure Handling
            t_end = time.perf_counter()
            duration = t_end - t_start
            meas_result = monitor.stop(artifacts_path=str(exp_dir))

            record.status = ExperimentStatus.FAILED
            record.decision = ResearchDecision.FAIL
            record.end_time = datetime.now(timezone.utc).isoformat()
            record.duration_seconds = round(duration, 6)
            record.failure_reason = str(exc)
            record.stack_trace = traceback.format_exc()
            record.metrics = meas_result.to_dict()

            logger.error(f"Experiment FAILED: {record.failure_reason}")
            logger.error(record.stack_trace)

        finally:
            try:
                active_engine.teardown()
            except Exception:
                pass

        # Step 8: Save metrics.json
        metrics_file = exp_dir / "metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(record.metrics, f, indent=2, sort_keys=True)

        # Step 9: Finalize logs
        logger.info("Flushing execution logs...")
        self._flush_logger(logger)

        # Record log telemetry
        line_count = 0
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                line_count = len(f.readlines())
        record.logs = {
            "log_file": str(log_file.relative_to(exp_dir)),
            "line_count": line_count,
        }

        # Step 10: Generate standardized report.md
        report_file = exp_dir / "report.md"
        ExperimentReporter.save_report(record, report_file)

        # Step 11: Catalog finalized artifacts (excluding metadata.json)
        record.artifacts = self._catalog_artifacts(exp_dir)

        # Step 12: Update registry and persist final metadata.json
        self.registry.register(record)

        return record

    def _setup_logger(self, exp_id: str, log_file: Path, level_str: str) -> logging.Logger:
        """Create an isolated logger writing directly to the experiment artifact directory."""
        logger_name = f"research.exp.{exp_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level_str.upper(), logging.INFO))
        logger.propagate = False

        # Clear existing handlers
        for h in list(logger.handlers):
            logger.removeHandler(h)

        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _flush_logger(self, logger: logging.Logger) -> None:
        """Flush and close handlers for logger."""
        for h in list(logger.handlers):
            try:
                h.flush()
                h.close()
                logger.removeHandler(h)
            except Exception:
                pass

    def _catalog_artifacts(self, exp_dir: Path) -> Dict[str, Any]:
        """Index all persistent files in the experiment directory, excluding metadata.json to prevent recursive hash modification."""
        import hashlib

        catalog: Dict[str, Any] = {}
        for root, _, files in os.walk(exp_dir):
            for f in sorted(files):
                if f == "metadata.json":
                    continue
                full_path = Path(root) / f
                rel_path = full_path.relative_to(exp_dir)
                size_bytes = full_path.stat().st_size

                # Compute sha256 for artifacts
                sha256 = ""
                try:
                    with open(full_path, "rb") as bf:
                        sha256 = hashlib.sha256(bf.read()).hexdigest()
                except Exception:
                    pass

                catalog[str(rel_path)] = {
                    "path": str(rel_path),
                    "bytes": size_bytes,
                    "sha256": sha256,
                }
        return catalog
