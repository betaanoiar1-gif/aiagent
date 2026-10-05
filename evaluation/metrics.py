"""Evaluation and Metric utilities for Phase 0 Research Foundation."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List


class MetricValidator:
    """Validates metrics schemas and integrity."""

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        """Compute SHA-256 hash."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def validate_metrics_dict(metrics: Dict[str, Any]) -> bool:
        """Ensure all required metric categories exist."""
        required = ["time", "cpu", "memory", "gpu", "disk"]
        return all(req in metrics for req in required)
