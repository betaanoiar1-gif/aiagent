"""Synthetic Model Implementation for Phase 0 Infrastructure Validation."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict

from models.base import BaseModel


class SyntheticBenchmarkModel(BaseModel):
    """Deterministic lightweight model representation for benchmark harness validation."""

    def __init__(
        self,
        identifier: str = "synthetic-baseline-v0",
        revision: str = "rev-001",
        parameter_count: int = 1_000_000,
    ) -> None:
        self._identifier = identifier
        self._revision = revision
        self._parameter_count = parameter_count
        self._is_loaded = False
        self._digest = hashlib.sha256(
            f"{identifier}:{revision}:{parameter_count}".encode("utf-8")
        ).hexdigest()

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def revision(self) -> str:
        return self._revision

    @property
    def parameter_count(self) -> int:
        return self._parameter_count

    def load(self) -> Dict[str, Any]:
        """Simulate deterministic model loading."""
        t0 = time.perf_counter()
        # Simulate slight deterministic load overhead
        time.sleep(0.01)
        t1 = time.perf_counter()
        self._is_loaded = True
        return {
            "model_identifier": self.identifier,
            "revision": self.revision,
            "parameter_count": self.parameter_count,
            "digest": self.get_digest(),
            "load_time_seconds": round(t1 - t0, 6),
        }

    def get_digest(self) -> str:
        return self._digest
