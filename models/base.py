"""Base Model interface for Phase 0 Research Foundation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """Abstract interface for all model wrappers."""

    @property
    @abstractmethod
    def identifier(self) -> str:
        """Model unique identifier."""
        pass

    @property
    @abstractmethod
    def revision(self) -> str:
        """Model revision / commit / checkpoint."""
        pass

    @property
    @abstractmethod
    def parameter_count(self) -> int:
        """Total parameters."""
        pass

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load model into memory and return loading telemetry."""
        pass

    @abstractmethod
    def get_digest(self) -> str:
        """Return cryptographic hash of model definition/weights."""
        pass
