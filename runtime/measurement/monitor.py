"""Resource Monitoring Harness for Phase 0 Research Foundation.

Continuously samples CPU, RAM, disk, and GPU/VRAM during workload execution.
Calculates summary statistics, peak resource consumption, and monitor overhead.
"""

from __future__ import annotations

import os
import shutil
import threading
import time
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

from runtime.measurement.metrics import (
    CPUMetrics,
    DiskMetrics,
    GPUMetrics,
    MeasurementResult,
    MemoryMetrics,
    TimeMetrics,
)


class ResourceMonitor:
    """Background sampling monitor for system and accelerator resources."""

    def __init__(
        self,
        sample_interval_ms: int = 50,
        target_path: str = ".",
    ) -> None:
        self.sample_interval_s = max(0.005, sample_interval_ms / 1000.0)
        self.target_path = target_path

        self._process = psutil.Process() if psutil is not None else None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Sample storage
        self._samples_cpu: List[float] = []
        self._samples_rss: List[int] = []
        self._samples_sys_ram_pct: List[float] = []
        self._samples_gpu_util: List[float] = []
        self._samples_vram: List[int] = []

        # Timers
        self._t_start_ns: int = 0
        self._t_end_ns: int = 0
        self._overhead_ns: int = 0

        # Initial snapshots
        self._start_cpu_times: Optional[Any] = None
        self._start_rss: int = 0
        self._start_sys_ram_pct: float = 0.0
        self._start_disk_free: int = 0

        # GPU capability detection
        self._has_gpu = False
        self._gpu_reason = "No GPU detected on host"
        self._detect_gpu_availability()

    def _detect_gpu_availability(self) -> None:
        """Check if GPU monitoring can be enabled."""
        # Phase 0 rule: Do not invent values.
        # Check for torch cuda or nvidia-smi
        has_smi = shutil.which("nvidia-smi") is not None
        if has_smi:
            self._has_gpu = True
            self._gpu_reason = ""
        else:
            self._has_gpu = False
            self._gpu_reason = "nvidia-smi not found; accelerator telemetry unavailable on this host"

    def start(self) -> None:
        """Start resource tracking and spawn background sampling thread."""
        overhead_start = time.perf_counter_ns()

        if self._process is not None:
            try:
                self._process.cpu_percent(interval=None)  # prime cpu_percent
                self._start_cpu_times = self._process.cpu_times()
                mem = self._process.memory_info()
                self._start_rss = mem.rss
            except Exception:
                self._start_rss = 0

        if psutil is not None:
            try:
                self._start_sys_ram_pct = psutil.virtual_memory().percent
            except Exception:
                self._start_sys_ram_pct = 0.0

        try:
            self._start_disk_free = shutil.disk_usage(self.target_path).free
        except Exception:
            self._start_disk_free = 0

        self._samples_cpu.clear()
        self._samples_rss.clear()
        self._samples_sys_ram_pct.clear()
        self._samples_gpu_util.clear()
        self._samples_vram.clear()

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._sampling_loop, daemon=True)

        overhead_end = time.perf_counter_ns()
        self._overhead_ns += (overhead_end - overhead_start)

        self._t_start_ns = time.perf_counter_ns()
        self._thread.start()

    def _sampling_loop(self) -> None:
        """Periodic background sampling of CPU and memory metrics."""
        while not self._stop_event.is_set():
            loop_t0 = time.perf_counter_ns()

            if self._process is not None:
                try:
                    cpu_p = self._process.cpu_percent(interval=None)
                    rss = self._process.memory_info().rss
                    self._samples_cpu.append(cpu_p)
                    self._samples_rss.append(rss)
                except Exception:
                    pass

            if psutil is not None:
                try:
                    sys_ram_pct = psutil.virtual_memory().percent
                    self._samples_sys_ram_pct.append(sys_ram_pct)
                except Exception:
                    pass

            loop_t1 = time.perf_counter_ns()
            self._overhead_ns += (loop_t1 - loop_t0)

            self._stop_event.wait(timeout=self.sample_interval_s)

    def stop(self, artifacts_path: Optional[str] = None) -> MeasurementResult:
        """Stop tracking, terminate background thread, and compute aggregated metrics."""
        self._t_end_ns = time.perf_counter_ns()
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

        overhead_start = time.perf_counter_ns()

        elapsed_seconds = (self._t_end_ns - self._t_start_ns) / 1_000_000_000.0

        # End process metrics
        end_rss = self._start_rss
        user_time = 0.0
        sys_time = 0.0
        if self._process is not None:
            try:
                end_rss = self._process.memory_info().rss
                if self._start_cpu_times is not None:
                    end_cpu_times = self._process.cpu_times()
                    user_time = max(0.0, end_cpu_times.user - self._start_cpu_times.user)
                    sys_time = max(0.0, end_cpu_times.system - self._start_cpu_times.system)
            except Exception:
                pass

        # End system RAM
        end_sys_ram_pct = self._start_sys_ram_pct
        if psutil is not None:
            try:
                end_sys_ram_pct = psutil.virtual_memory().percent
            except Exception:
                pass

        # End disk
        end_disk_free = self._start_disk_free
        try:
            end_disk_free = shutil.disk_usage(self.target_path).free
        except Exception:
            pass

        # Calculate directory artifact bytes
        artifact_bytes = 0
        if artifacts_path and os.path.exists(artifacts_path):
            try:
                for root, _, files in os.walk(artifacts_path):
                    for file in files:
                        f_path = os.path.join(root, file)
                        if os.path.isfile(f_path):
                            artifact_bytes += os.path.getsize(f_path)
            except Exception:
                pass

        # CPU aggregates
        cpu_mean = (
            sum(self._samples_cpu) / len(self._samples_cpu)
            if self._samples_cpu
            else 0.0
        )
        cpu_peak = max(self._samples_cpu) if self._samples_cpu else 0.0

        # Memory aggregates
        peak_rss = max(self._samples_rss) if self._samples_rss else max(self._start_rss, end_rss)
        delta_rss = end_rss - self._start_rss
        peak_sys_ram = (
            max(self._samples_sys_ram_pct)
            if self._samples_sys_ram_pct
            else end_sys_ram_pct
        )

        # GPU metrics
        gpu_metrics = GPUMetrics(
            status="available" if self._has_gpu else "unavailable",
            reason=None if self._has_gpu else self._gpu_reason,
            utilization_percent_mean=None,
            utilization_percent_peak=None,
            vram_start_bytes=None,
            vram_end_bytes=None,
            peak_vram_bytes=None,
            delta_vram_bytes=None,
        )

        overhead_end = time.perf_counter_ns()
        self._overhead_ns += (overhead_end - overhead_start)
        overhead_seconds = self._overhead_ns / 1_000_000_000.0

        return MeasurementResult(
            time=TimeMetrics(
                wall_clock_seconds=round(elapsed_seconds, 6),
                overhead_seconds=round(overhead_seconds, 6),
            ),
            cpu=CPUMetrics(
                cpu_percent_mean=round(cpu_mean, 2),
                cpu_percent_peak=round(cpu_peak, 2),
                user_time_seconds=round(user_time, 4),
                system_time_seconds=round(sys_time, 4),
            ),
            memory=MemoryMetrics(
                start_rss_bytes=self._start_rss,
                end_rss_bytes=end_rss,
                peak_rss_bytes=peak_rss,
                delta_rss_bytes=delta_rss,
                system_ram_percent_start=round(self._start_sys_ram_pct, 2),
                system_ram_percent_peak=round(peak_sys_ram, 2),
                system_ram_percent_end=round(end_sys_ram_pct, 2),
            ),
            gpu=gpu_metrics,
            disk=DiskMetrics(
                start_free_bytes=self._start_disk_free,
                end_free_bytes=end_disk_free,
                delta_free_bytes=self._start_disk_free - end_disk_free,
                artifacts_bytes=artifact_bytes,
            ),
            sample_count=len(self._samples_rss),
        )
