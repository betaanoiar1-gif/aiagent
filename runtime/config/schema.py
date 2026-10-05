"""Experiment Schema definitions and enums for Phase 0 Research Foundation.

Implements the mandatory scientific registry contract: every experiment record
guarantees complete traceability, immutability, and reproducibility.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class ExperimentStatus(str, Enum):
    """Experiment lifecycle states."""
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ResearchDecision(str, Enum):
    """Scientific validation decision outcomes."""
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class ExperimentRecord:
    """The central unified record of an individual scientific experiment."""
    # Mandatory core identification & hypothesis
    experiment_id: str
    experiment_name: str
    hypothesis: str
    objective: str

    # Timing & State
    timestamp: str  # ISO-8601 UTC creation time
    status: ExperimentStatus = ExperimentStatus.CREATED
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None

    # Versioning & Traceability
    git_commit: str = ""
    git_branch: str = ""
    git_is_dirty: bool = False
    hardware_fingerprint: str = ""
    software_fingerprint: str = ""
    software_environment: Dict[str, Any] = field(default_factory=dict)
    hardware_profile: Dict[str, Any] = field(default_factory=dict)

    # Scientific Inputs & Models
    model_identifier: str = ""
    model_revision: str = ""
    random_seed: int = 0
    input_reference: Dict[str, Any] = field(default_factory=dict)
    output_reference: Dict[str, Any] = field(default_factory=dict)

    # Configurations
    configuration: Dict[str, Any] = field(default_factory=dict)
    runtime_configuration: Dict[str, Any] = field(default_factory=dict)

    # Execution telemetry & results
    metrics: Dict[str, Any] = field(default_factory=dict)
    logs: Dict[str, Any] = field(default_factory=dict)  # Log file references & summary
    artifacts: Dict[str, Any] = field(default_factory=dict)  # Artifact name -> metadata

    # Scientific Evaluation & Outcome
    decision: ResearchDecision = ResearchDecision.PENDING
    notes: str = ""
    failure_reason: Optional[str] = None
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to a JSON-serializable dictionary."""
        data = asdict(self)
        data["status"] = self.status.value if isinstance(self.status, ExperimentStatus) else str(self.status)
        data["decision"] = self.decision.value if isinstance(self.decision, ResearchDecision) else str(self.decision)
        return data

    def to_json(self, indent: int = 2) -> str:
        """Serialize record to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentRecord":
        """Instantiate ExperimentRecord from dictionary."""
        d = dict(data)
        if "status" in d and isinstance(d["status"], str):
            d["status"] = ExperimentStatus(d["status"])
        if "decision" in d and isinstance(d["decision"], str):
            d["decision"] = ResearchDecision(d["decision"])
        return cls(**d)
