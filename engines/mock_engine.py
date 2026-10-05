"""Deterministic Synthetic Benchmark Engine for Phase 0 Infrastructure Validation.

Executes mathematically reproducible synthetic workloads to validate timing,
resource measurement, failure recovery, and artifact management without
introducing Phase 1 generation optimizations or heavy unverified model weights.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from engines.base import BaseEngine


class DeterministicSyntheticEngine(BaseEngine):
    """Synthetic deterministic engine for baseline harness verification."""

    def __init__(self) -> None:
        self.is_initialized = False
        self.engine_config: Dict[str, Any] = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize engine parameters."""
        self.engine_config = dict(config)
        self.is_initialized = True

    def execute(
        self,
        workload_params: Dict[str, Any],
        random_seed: int,
        output_dir: str,
    ) -> Dict[str, Any]:
        """Execute deterministic pseudo-workload."""
        if not self.is_initialized:
            raise RuntimeError("DeterministicSyntheticEngine must be initialized before execution")

        # 1. Failure simulation support for robust lifecycle testing
        if workload_params.get("simulate_failure", False):
            failure_step = workload_params.get("failure_step", 1)
            error_msg = workload_params.get(
                "failure_message",
                f"Simulated workload exception at step {failure_step}",
            )
            raise RuntimeError(f"EngineExecutionFailure: {error_msg}")

        iterations = int(workload_params.get("iterations", 1000))
        matrix_size = int(workload_params.get("matrix_size", 64))

        # Linear Congruential Generator for reproducible pseudo-random sequence
        a = 1664525
        c = 1013904223
        m = 2**32
        state = (random_seed + 1) & 0xFFFFFFFF

        grid: List[float] = [0.0] * (matrix_size * matrix_size)
        total_accum = 0.0

        for it in range(iterations):
            # Update state
            state = (a * state + c) % m
            val = (state / float(m)) * 2.0 - 1.0
            idx = state % len(grid)
            grid[idx] = (grid[idx] * 0.95) + (val * 0.05)
            total_accum += math.sin(val)

        # Convert final grid to bytes
        raw_bytes = bytearray()
        for v in grid:
            norm = int(((math.sin(v) + 1.0) / 2.0) * 255.0) & 0xFF
            raw_bytes.append(norm)

        # Generate deterministic output PPM image
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        image_path = out_path / "synthetic_feature_map.ppm"

        # PPM header: P6 <width> <height> <maxval>\n
        ppm_header = f"P6\n{matrix_size} {matrix_size}\n255\n".encode("ascii")
        ppm_body = bytearray()
        for b in raw_bytes:
            # R, G, B channels
            ppm_body.extend([b, (b * 3) % 256, (b * 7) % 256])

        with open(image_path, "wb") as f:
            f.write(ppm_header)
            f.write(ppm_body)

        full_content = ppm_header + ppm_body
        content_hash = hashlib.sha256(full_content).hexdigest()

        # Write output manifest
        manifest_path = out_path / "output_manifest.json"
        manifest_data = {
            "random_seed": random_seed,
            "matrix_size": matrix_size,
            "iterations": iterations,
            "accumulator_sum": round(total_accum, 6),
            "output_sha256": content_hash,
            "output_files": [
                {
                    "name": "synthetic_feature_map.ppm",
                    "bytes": len(full_content),
                    "sha256": content_hash,
                }
            ],
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        return {
            "status": "COMPLETED",
            "iterations_completed": iterations,
            "matrix_size": matrix_size,
            "accumulator_sum": round(total_accum, 6),
            "output_sha256": content_hash,
            "artifact_path": str(image_path),
            "artifact_bytes": len(full_content),
            "manifest_path": str(manifest_path),
        }

    def teardown(self) -> None:
        """Clean up."""
        self.is_initialized = False
        self.engine_config.clear()
