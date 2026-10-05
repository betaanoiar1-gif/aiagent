"""Resource Measurement Metrics data structures for Phase 0 Research Foundation.

Captures wall-clock time, CPU, RAM, GPU/VRAM, disk, model load time,
inference time, and measurement overhead.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class TimeMetrics:
    """Detailed wall-clock timing breakdown."""
    wall_clock_seconds: float = 0.0
    model_load_seconds: float = 0.0
    inference_seconds: float = 0.0
    pre_process_seconds: float = 0.0
    post_process_seconds: float = 0.0
    overhead_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CPUMetrics:
    """CPU telemetry metrics."""
    cpu_percent_mean: float = 0.0
    cpu_percent_peak: float = 0.0
    user_time_seconds: float = 0.0
    system_time_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryMetrics:
    """Host RAM telemetry metrics."""
    start_rss_bytes: int = 0
    end_rss_bytes: int = 0
    peak_rss_bytes: int = 0
    delta_rss_bytes: int = 0
    system_ram_percent_start: float = 0.0
    system_ram_percent_peak: float = 0.0
    system_ram_percent_end: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GPUMetrics:
    """GPU / VRAM telemetry metrics."""
    status: str = "unavailable"
    reason: Optional[str] = "No GPU detected on host"
    utilization_percent_mean: Optional[float] = None
    utilization_percent_peak: Optional[float] = None
    vram_start_bytes: Optional[int] = None
    vram_end_bytes: Optional[int] = None
    peak_vram_bytes: Optional[int] = None
    delta_vram_bytes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiskMetrics:
    """Disk storage footprint metrics."""
    start_free_bytes: int = 0
    end_free_bytes: int = 0
    delta_free_bytes: int = 0
    artifacts_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeasurementResult:
    """Comprehensive aggregation of all telemetry measurements."""
    time: TimeMetrics = field(default_factory=TimeMetrics)
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    gpu: GPUMetrics = field(default_factory=GPUMetrics)
    disk: DiskMetrics = field(default_factory=DiskMetrics)
    workload_metrics: Dict[str, Any] = field(default_factory=dict)
    sample_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time.to_dict(),
            "cpu": self.cpu.to_dict(),
            "memory": self.memory.to_dict(),
            "gpu": self.gpu.to_dict(),
            "disk": self.disk.to_dict(),
            "workload_metrics": self.workload_metrics,
            "sample_count": self.sample_count,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
