"""Validation tests for Hardware Profiler and Fingerprint generation."""

import json
from runtime.profiler.hardware import HardwareAttribute, HardwareProfile, HardwareProfiler


def test_hardware_profiler_discovery():
    """Verify hardware profiler discovers host specs without fabricating values."""
    profiler = HardwareProfiler()
    profile = profiler.profile()

    # CPU verification
    assert profile.cpu_model.value is not None
    assert profile.cpu_cores_physical.value >= 1
    assert profile.cpu_cores_logical.value >= profile.cpu_cores_physical.value

    # RAM verification
    assert profile.ram_total_bytes.value > 0
    assert profile.ram_available_bytes.value > 0
    assert profile.ram_available_bytes.value <= profile.ram_total_bytes.value

    # Disk verification
    assert profile.disk_capacity_bytes.value > 0
    assert profile.disk_free_bytes.value > 0

    # Platform & Python
    assert profile.os_name.value in {"Linux", "Darwin", "Windows"}
    assert profile.python_version.value.startswith("3.")

    # Accelerator discovery check (No GPU on this container)
    if profile.gpu_count.value == 0:
        assert profile.gpu_name.status == "unavailable"
        assert profile.gpu_name.reason is not None
        assert "No NVIDIA GPU" in profile.gpu_name.reason or "not found" in profile.gpu_name.reason
        assert profile.cuda_version.status == "unavailable"
    else:
        assert profile.gpu_name.status == "available"


def test_hardware_fingerprint_determinism():
    """Verify hardware fingerprint is strictly deterministic across repeated calls."""
    profiler = HardwareProfiler()
    p1 = profiler.profile()
    p2 = profiler.profile()

    assert p1.hardware_fingerprint.startswith("hwfp_")
    assert len(p1.hardware_fingerprint) > 10
    assert p1.hardware_fingerprint == p2.hardware_fingerprint


def test_hardware_fingerprint_sensitivity():
    """Verify hardware fingerprint changes if immutable hardware specs differ."""
    profiler = HardwareProfiler()
    p1 = profiler.profile()

    # Create synthetic modified profile
    p2_dict = p1.to_dict()
    # Modify physical cores
    p2 = profiler.profile()
    p2.cpu_cores_physical = HardwareAttribute.available(p1.cpu_cores_physical.value + 4)
    fp_modified = profiler.compute_fingerprint(p2)

    assert p1.hardware_fingerprint != fp_modified


def test_hardware_profile_serialization():
    """Verify JSON serialization and dictionary conversion integrity."""
    profiler = HardwareProfiler()
    profile = profiler.profile()

    d = profile.to_dict()
    assert isinstance(d, dict)
    assert "hardware_fingerprint" in d
    assert d["cpu_model"]["status"] == "available"

    j = profile.to_json()
    loaded = json.loads(j)
    assert loaded["hardware_fingerprint"] == profile.hardware_fingerprint
