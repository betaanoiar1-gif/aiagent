"""Validation tests for Resource Monitoring and Telemetry layer."""

import time
from runtime.measurement.monitor import ResourceMonitor


def test_resource_monitor_timing_and_memory():
    """Verify ResourceMonitor captures wall-clock time, RSS memory, and overhead."""
    monitor = ResourceMonitor(sample_interval_ms=10)
    monitor.start()

    # Perform lightweight measurable memory work
    block = [i * 2 for i in range(200_000)]
    time.sleep(0.05)

    result = monitor.stop()

    assert result.time.wall_clock_seconds >= 0.04
    assert result.time.overhead_seconds >= 0.0
    assert result.memory.peak_rss_bytes > 0
    assert result.memory.start_rss_bytes > 0
    assert result.cpu.cpu_percent_peak >= 0.0
    assert result.sample_count >= 1


def test_resource_monitor_gpu_status_reporting():
    """Verify GPU status is reported truthfully without fabricating metrics."""
    monitor = ResourceMonitor()
    monitor.start()
    time.sleep(0.01)
    result = monitor.stop()

    assert result.gpu.status in {"available", "unavailable"}
    if result.gpu.status == "unavailable":
        assert result.gpu.reason is not None
        assert result.gpu.peak_vram_bytes is None
