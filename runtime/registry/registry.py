"""Experiment Registry for Phase 0 Research Foundation.

Provides centralized registration, persistent indexing, query capabilities,
and artifact path resolution for all scientific experiments.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from runtime.config.experiment_config import ExperimentConfig
from runtime.config.runtime_config import RuntimeConfig
from runtime.config.schema import (
    ExperimentRecord,
    ExperimentStatus,
    ResearchDecision,
)


class ExperimentRegistry:
    """Thread-safe registry for persisting and retrieving experiment records."""

    def __init__(self, base_dir: str = "research/experiments") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.registry_index_path = self.base_dir / "registry.json"
        self._lock = threading.Lock()
        self._ensure_index_exists()

    def _ensure_index_exists(self) -> None:
        with self._lock:
            if not self.registry_index_path.exists():
                with open(self.registry_index_path, "w", encoding="utf-8") as f:
                    json.dump({"experiments": [], "last_index": 0}, f, indent=2)

    def _read_index(self) -> Dict[str, Any]:
        with open(self.registry_index_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {"experiments": [], "last_index": 0}

    def _write_index(self, data: Dict[str, Any]) -> None:
        temp_path = self.registry_index_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(temp_path, self.registry_index_path)

    def allocate_experiment_id(self, prefix: str = "EXP") -> str:
        """Atomically generate the next sequential experiment ID."""
        with self._lock:
            index_data = self._read_index()
            next_idx = int(index_data.get("last_index", 0)) + 1
            exp_id = f"{prefix}-{next_idx:06d}"
            # Check if directory already exists, if so increment until free
            while (self.base_dir / exp_id).exists():
                next_idx += 1
                exp_id = f"{prefix}-{next_idx:06d}"

            index_data["last_index"] = next_idx
            self._write_index(index_data)
            return exp_id

    def get_experiment_dir(self, experiment_id: str) -> Path:
        """Resolve directory path for an experiment."""
        return self.base_dir / experiment_id

    def register(self, record: ExperimentRecord) -> None:
        """Register or update an experiment in the central index and write metadata."""
        exp_dir = self.get_experiment_dir(record.experiment_id)
        exp_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write metadata.json inside the experiment directory
        metadata_file = exp_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(record.to_json(indent=2))

        # 2. Update central index
        with self._lock:
            index_data = self._read_index()
            experiments: List[Dict[str, Any]] = index_data.get("experiments", [])

            summary = {
                "experiment_id": record.experiment_id,
                "experiment_name": record.experiment_name,
                "hypothesis": record.hypothesis,
                "status": record.status.value if isinstance(record.status, ExperimentStatus) else str(record.status),
                "decision": record.decision.value if isinstance(record.decision, ResearchDecision) else str(record.decision),
                "timestamp": record.timestamp,
                "git_commit": record.git_commit,
                "hardware_fingerprint": record.hardware_fingerprint,
                "software_fingerprint": record.software_fingerprint,
                "model_identifier": record.model_identifier,
                "random_seed": record.random_seed,
                "duration_seconds": record.duration_seconds,
                "path": str(exp_dir),
            }

            # Update existing or append
            found = False
            for i, item in enumerate(experiments):
                if item.get("experiment_id") == record.experiment_id:
                    experiments[i] = summary
                    found = True
                    break
            if not found:
                experiments.append(summary)

            index_data["experiments"] = experiments
            self._write_index(index_data)

    def get(self, experiment_id: str) -> Optional[ExperimentRecord]:
        """Retrieve full ExperimentRecord by experiment_id."""
        exp_dir = self.get_experiment_dir(experiment_id)
        metadata_file = exp_dir / "metadata.json"
        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ExperimentRecord.from_dict(data)
        except Exception:
            return None

    def exists(self, experiment_id: str) -> bool:
        """Check if an experiment ID exists."""
        return (self.get_experiment_dir(experiment_id) / "metadata.json").exists()

    def list(
        self,
        status: Optional[ExperimentStatus] = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List experiments matching filters."""
        with self._lock:
            index_data = self._read_index()
            experiments: List[Dict[str, Any]] = index_data.get("experiments", [])

        results = []
        for item in experiments:
            if status is not None:
                item_status = item.get("status")
                target_status = status.value if isinstance(status, ExperimentStatus) else str(status)
                if item_status != target_status:
                    continue

            if query:
                q_lower = query.lower()
                matched = (
                    q_lower in item.get("experiment_id", "").lower()
                    or q_lower in item.get("experiment_name", "").lower()
                    or q_lower in item.get("hypothesis", "").lower()
                    or q_lower in item.get("model_identifier", "").lower()
                )
                if not matched:
                    continue

            results.append(item)

        if limit is not None and limit > 0:
            results = results[-limit:]

        return results
