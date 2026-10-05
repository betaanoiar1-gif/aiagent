"""Base Engine interface for research workloads."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseEngine(ABC):
    """Abstract interface for all research execution engines."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize engine resources."""
        pass

    @abstractmethod
    def execute(
        self,
        workload_params: Dict[str, Any],
        random_seed: int,
        output_dir: str,
    ) -> Dict[str, Any]:
        """Execute workload and return result dictionary including artifact references."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Release all allocated engine resources."""
        pass
