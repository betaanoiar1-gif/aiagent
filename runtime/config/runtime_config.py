"""Runtime Configuration for Phase 0 Research Foundation.

Controls runner execution behavior, resource monitoring frequency, timeouts,
and output directories without affecting the scientific hypothesis or parameters.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Union


@dataclass
class RuntimeConfig:
    """Settings controlling experiment execution, monitoring, and output paths."""
    output_dir: str = "research/experiments"
    timeout_seconds: float = 300.0
    sample_interval_ms: int = 50
    log_level: str = "INFO"
    record_hardware: bool = True
    record_software: bool = True
    save_artifacts: bool = True
    deterministic_mode: bool = True
    allow_failure_recovery: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def save_json(self, path: Union[str, Path]) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuntimeConfig":
        return cls(
            output_dir=str(data.get("output_dir", "research/experiments")),
            timeout_seconds=float(data.get("timeout_seconds", 300.0)),
            sample_interval_ms=int(data.get("sample_interval_ms", 50)),
            log_level=str(data.get("log_level", "INFO")),
            record_hardware=bool(data.get("record_hardware", True)),
            record_software=bool(data.get("record_software", True)),
            save_artifacts=bool(data.get("save_artifacts", True)),
            deterministic_mode=bool(data.get("deterministic_mode", True)),
            allow_failure_recovery=bool(data.get("allow_failure_recovery", True)),
        )

    @classmethod
    def from_json_file(cls, path: Union[str, Path]) -> "RuntimeConfig":
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"Runtime config file not found: {path}")
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
