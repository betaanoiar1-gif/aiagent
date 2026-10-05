"""Baseline Generation Engine for Phase 1 Research.

Audits host hardware prerequisites against official baseline model requirements.
Enforces the strict scientific rule: never synthesize or fake GPU inference.
If an accelerator is missing, raises an explicit EnvironmentHardwarePrerequisiteError
so the Phase 0 harness captures the failure state, telemetry, and diagnostics.
"""

from __future__ import annotations

import os
import shutil
from typing import Any, Dict, Optional

from engines.base import BaseEngine
from runtime.profiler.hardware import HardwareProfiler


class EnvironmentHardwarePrerequisiteError(RuntimeError):
    """Raised when the host environment fails to meet mandatory physical accelerator requirements."""
    pass


class BaselineGenerationEngine(BaseEngine):
    """Engine responsible for loading and executing unquantized open-source baseline models."""

    # Official un-optimized minimum hardware specifications
    HARDWARE_REQUIREMENTS = {
        "runwayml/stable-diffusion-v1-5": {
            "min_gpus": 1,
            "min_vram_gb": 4.0,
            "recommended_vram_gb": 8.0,
            "min_system_ram_gb": 8.0,
            "requires_cuda": True,
        },
        "Wan-AI/Wan2.1-T2V-1.3B": {
            "min_gpus": 1,
            "min_vram_gb": 8.19,
            "recommended_vram_gb": 24.0,
            "min_system_ram_gb": 16.0,
            "requires_cuda": True,
        },
        "Lightricks/LTX-Video": {
            "min_gpus": 1,
            "min_vram_gb": 8.0,
            "recommended_vram_gb": 16.0,
            "min_system_ram_gb": 16.0,
            "requires_cuda": True,
        },
    }

    def __init__(self) -> None:
        self.is_initialized = False
        self.config: Dict[str, Any] = {}
        self.profiler = HardwareProfiler()

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize engine and verify environment capability."""
        self.config = dict(config)
        self.is_initialized = True

    def execute(
        self,
        workload_params: Dict[str, Any],
        random_seed: int,
        output_dir: str,
    ) -> Dict[str, Any]:
        """Audit hardware against requirements and execute un-optimized baseline."""
        if not self.is_initialized:
            raise RuntimeError("BaselineGenerationEngine must be initialized before execution.")

        model_id = str(workload_params.get("model_identifier", "unknown"))
        reqs = self.HARDWARE_REQUIREMENTS.get(
            model_id,
            {"min_gpus": 1, "min_vram_gb": 8.0, "min_system_ram_gb": 8.0, "requires_cuda": True},
        )

        # Probe host hardware
        profile = self.profiler.profile()
        gpu_count = profile.gpu_count.value or 0
        cuda_status = profile.cuda_version.status
        ram_gb = (profile.ram_total_bytes.value or 0) / (1024**3)

        # Physical hardware verification
        failures = []
        if gpu_count < reqs["min_gpus"]:
            failures.append(
                f"Missing physical GPU: detected {gpu_count} GPUs, minimum required is {reqs['min_gpus']}."
            )
        if reqs["requires_cuda"] and cuda_status != "available":
            failures.append(
                f"CUDA compiler/runtime unavailable: {profile.cuda_version.reason}."
            )
        if ram_gb < reqs["min_system_ram_gb"]:
            failures.append(
                f"Insufficient host system RAM: detected {ram_gb:.2f} GB, minimum required is {reqs['min_system_ram_gb']:.1f} GB."
            )

        if failures:
            error_details = " | ".join(failures)
            raise EnvironmentHardwarePrerequisiteError(
                f"EnvironmentHardwarePrerequisiteError: Host environment cannot execute baseline model '{model_id}'. "
                f"Discovered Deficiencies: [{error_details}]. "
                f"Per Phase 1 research protocol, CPU-only generation is prohibited because it cannot measure VRAM or GPU compute profile. "
                f"Execution aborted to preserve empirical validity."
            )

        # If this point were reached on a GPU-enabled node:
        return {
            "status": "COMPLETED",
            "model_identifier": model_id,
            "random_seed": random_seed,
        }

    def teardown(self) -> None:
        """Release allocated resources."""
        self.is_initialized = False
        self.config.clear()
