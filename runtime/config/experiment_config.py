"""Experiment Configuration for Phase 0 Research Foundation.

Represents pure experiment specifications, completely decoupled from runtime
settings or environment metadata.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentConfig:
    """Specification of a scientific experiment."""
    experiment_name: str
    hypothesis: str
    objective: str
    model_identifier: str
    model_revision: str
    random_seed: int
    workload_type: str = "synthetic_matrix"
    workload_params: Dict[str, Any] = field(default_factory=dict)
    input_reference: Dict[str, Any] = field(default_factory=dict)
    output_reference: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    experiment_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def save_json(self, path: Union[str, Path]) -> None:
        """Write configuration to JSON file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentConfig":
        """Instantiate from dictionary with validation."""
        required = [
            "experiment_name",
            "hypothesis",
            "objective",
            "model_identifier",
            "model_revision",
            "random_seed",
        ]
        missing = [f for f in required if f not in data]
        if missing:
            raise ValueError(f"Missing required ExperimentConfig fields: {missing}")

        return cls(
            experiment_name=str(data["experiment_name"]),
            hypothesis=str(data["hypothesis"]),
            objective=str(data["objective"]),
            model_identifier=str(data["model_identifier"]),
            model_revision=str(data["model_revision"]),
            random_seed=int(data["random_seed"]),
            workload_type=str(data.get("workload_type", "synthetic_matrix")),
            workload_params=dict(data.get("workload_params", {})),
            input_reference=dict(data.get("input_reference", {})),
            output_reference=dict(data.get("output_reference", {})),
            tags=list(data.get("tags", [])),
            notes=str(data.get("notes", "")),
            experiment_id=data.get("experiment_id"),
        )

    @classmethod
    def from_json_file(cls, path: Union[str, Path]) -> "ExperimentConfig":
        """Load from a JSON file path."""
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
