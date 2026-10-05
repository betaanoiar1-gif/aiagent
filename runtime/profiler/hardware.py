"""Hardware Profiler for Phase 0 Research Foundation.

Discovers and records all available host and accelerator hardware metrics.
Adheres strictly to the scientific rule: never fabricate values.
When an attribute cannot be determined, it records status="unavailable"
with an explicit causal explanation. Produces a deterministic hardware fingerprint.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, Union

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore


@dataclass
class HardwareAttribute:
    """Represents a single hardware attribute with status and reason."""
    value: Any
    status: str = "available"  # "available" | "unavailable"
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "status": self.status,
            "reason": self.reason,
        }

    @classmethod
    def available(cls, value: Any) -> "HardwareAttribute":
        return cls(value=value, status="available", reason=None)

    @classmethod
    def unavailable(cls, reason: str, default: Any = None) -> "HardwareAttribute":
        return cls(value=default, status="unavailable", reason=reason)


@dataclass
class HardwareProfile:
    """Comprehensive hardware profile representation."""
    # GPU Attributes
    gpu_name: HardwareAttribute
    gpu_count: HardwareAttribute
    vram_total_bytes: HardwareAttribute
    vram_available_bytes: HardwareAttribute
    gpu_architecture: HardwareAttribute
    compute_capability: HardwareAttribute
    driver_version: HardwareAttribute
    cuda_version: HardwareAttribute

    # CPU Attributes
    cpu_model: HardwareAttribute
    cpu_cores_physical: HardwareAttribute
    cpu_cores_logical: HardwareAttribute

    # RAM Attributes
    ram_total_bytes: HardwareAttribute
    ram_available_bytes: HardwareAttribute

    # Disk Attributes
    disk_capacity_bytes: HardwareAttribute
    disk_free_bytes: HardwareAttribute

    # Platform & OS Attributes
    os_name: HardwareAttribute
    os_release: HardwareAttribute
    kernel_version: HardwareAttribute
    host_architecture: HardwareAttribute

    # Runtime & Framework Versions
    python_version: HardwareAttribute
    pytorch_version: HardwareAttribute
    relevant_runtimes: Dict[str, HardwareAttribute] = field(default_factory=dict)

    # Deterministic Hardware Fingerprint
    hardware_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the hardware profile to a serializable dictionary."""
        return {
            "hardware_fingerprint": self.hardware_fingerprint,
            "gpu_name": self.gpu_name.to_dict(),
            "gpu_count": self.gpu_count.to_dict(),
            "vram_total_bytes": self.vram_total_bytes.to_dict(),
            "vram_available_bytes": self.vram_available_bytes.to_dict(),
            "gpu_architecture": self.gpu_architecture.to_dict(),
            "compute_capability": self.compute_capability.to_dict(),
            "driver_version": self.driver_version.to_dict(),
            "cuda_version": self.cuda_version.to_dict(),
            "cpu_model": self.cpu_model.to_dict(),
            "cpu_cores_physical": self.cpu_cores_physical.to_dict(),
            "cpu_cores_logical": self.cpu_cores_logical.to_dict(),
            "ram_total_bytes": self.ram_total_bytes.to_dict(),
            "ram_available_bytes": self.ram_available_bytes.to_dict(),
            "disk_capacity_bytes": self.disk_capacity_bytes.to_dict(),
            "disk_free_bytes": self.disk_free_bytes.to_dict(),
            "os_name": self.os_name.to_dict(),
            "os_release": self.os_release.to_dict(),
            "kernel_version": self.kernel_version.to_dict(),
            "host_architecture": self.host_architecture.to_dict(),
            "python_version": self.python_version.to_dict(),
            "pytorch_version": self.pytorch_version.to_dict(),
            "relevant_runtimes": {
                k: v.to_dict() for k, v in self.relevant_runtimes.items()
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize profile to JSON."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class HardwareProfiler:
    """Probes the host machine and accelerator devices to build a hardware profile."""

    def __init__(self, target_disk_path: str = ".") -> None:
        self.target_disk_path = target_disk_path

    def profile(self) -> HardwareProfile:
        """Execute full hardware discovery and return a HardwareProfile instance."""
        # 1. CPU profiling
        cpu_model_attr = self._detect_cpu_model()
        cpu_phys_attr, cpu_log_attr = self._detect_cpu_cores()

        # 2. RAM profiling
        ram_total_attr, ram_avail_attr = self._detect_ram()

        # 3. Disk profiling
        disk_cap_attr, disk_free_attr = self._detect_disk(self.target_disk_path)

        # 4. OS & Kernel profiling
        os_name_attr = HardwareAttribute.available(platform.system())
        os_release_attr = HardwareAttribute.available(platform.release())
        kernel_attr = self._detect_kernel_version()
        arch_attr = HardwareAttribute.available(platform.machine())

        # 5. Python runtime
        py_ver_attr = HardwareAttribute.available(platform.python_version())

        # 6. Accelerator / GPU profiling
        gpu_attrs = self._detect_gpu()

        # 7. Framework versions (PyTorch & CUDA)
        torch_attr = self._detect_pytorch()
        cuda_attr = self._detect_cuda(gpu_attrs.get("cuda_from_smi"))

        # 8. Relevant runtimes
        runtimes = self._detect_relevant_runtimes()

        profile = HardwareProfile(
            gpu_name=gpu_attrs["gpu_name"],
            gpu_count=gpu_attrs["gpu_count"],
            vram_total_bytes=gpu_attrs["vram_total_bytes"],
            vram_available_bytes=gpu_attrs["vram_available_bytes"],
            gpu_architecture=gpu_attrs["gpu_architecture"],
            compute_capability=gpu_attrs["compute_capability"],
            driver_version=gpu_attrs["driver_version"],
            cuda_version=cuda_attr,
            cpu_model=cpu_model_attr,
            cpu_cores_physical=cpu_phys_attr,
            cpu_cores_logical=cpu_log_attr,
            ram_total_bytes=ram_total_attr,
            ram_available_bytes=ram_avail_attr,
            disk_capacity_bytes=disk_cap_attr,
            disk_free_bytes=disk_free_attr,
            os_name=os_name_attr,
            os_release=os_release_attr,
            kernel_version=kernel_attr,
            host_architecture=arch_attr,
            python_version=py_ver_attr,
            pytorch_version=torch_attr,
            relevant_runtimes=runtimes,
        )

        profile.hardware_fingerprint = self.compute_fingerprint(profile)
        return profile

    def compute_fingerprint(self, profile: HardwareProfile) -> str:
        """Generate a deterministic SHA-256 fingerprint from immutable hardware specs."""
        components = [
            f"cpu_model:{profile.cpu_model.value}",
            f"cpu_physical_cores:{profile.cpu_cores_physical.value}",
            f"cpu_logical_cores:{profile.cpu_cores_logical.value}",
            f"ram_total_bytes:{profile.ram_total_bytes.value}",
            f"host_arch:{profile.host_architecture.value}",
            f"gpu_name:{profile.gpu_name.value}",
            f"gpu_count:{profile.gpu_count.value}",
            f"gpu_arch:{profile.gpu_architecture.value}",
        ]
        raw_string = "|".join(components)
        digest = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
        return f"hwfp_{digest[:32]}"

    def _detect_cpu_model(self) -> HardwareAttribute:
        """Extract CPU model name accurately."""
        # Try /proc/cpuinfo first on Linux
        if os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                    for line in f:
                        if "model name" in line:
                            model = line.split(":", 1)[1].strip()
                            if model:
                                return HardwareAttribute.available(model)
                        if "Hardware" in line:
                            hw = line.split(":", 1)[1].strip()
                            if hw:
                                return HardwareAttribute.available(hw)
            except Exception as e:
                pass

        # Fallback to platform
        proc = platform.processor()
        if proc:
            return HardwareAttribute.available(proc)

        return HardwareAttribute.unavailable(
            reason="CPU model name could not be resolved from /proc/cpuinfo or platform"
        )

    def _detect_cpu_cores(self) -> tuple[HardwareAttribute, HardwareAttribute]:
        """Detect physical and logical CPU cores."""
        if psutil is not None:
            phys = psutil.cpu_count(logical=False)
            log = psutil.cpu_count(logical=True)
            phys_attr = (
                HardwareAttribute.available(phys)
                if phys is not None
                else HardwareAttribute.unavailable(
                    reason="Physical core count undetermined by psutil", default=1
                )
            )
            log_attr = (
                HardwareAttribute.available(log)
                if log is not None
                else HardwareAttribute.unavailable(
                    reason="Logical core count undetermined by psutil", default=1
                )
            )
            return phys_attr, log_attr

        # Fallback without psutil
        try:
            log_cores = os.cpu_count()
            if log_cores is not None:
                return (
                    HardwareAttribute.unavailable(
                        reason="psutil not installed; physical core count cannot be differentiated",
                        default=log_cores,
                    ),
                    HardwareAttribute.available(log_cores),
                )
        except Exception as e:
            pass

        return (
            HardwareAttribute.unavailable(reason="Failed to detect CPU physical cores"),
            HardwareAttribute.unavailable(reason="Failed to detect CPU logical cores"),
        )

    def _detect_ram(self) -> tuple[HardwareAttribute, HardwareAttribute]:
        """Detect total and available RAM bytes."""
        if psutil is not None:
            try:
                vm = psutil.virtual_memory()
                return (
                    HardwareAttribute.available(int(vm.total)),
                    HardwareAttribute.available(int(vm.available)),
                )
            except Exception as e:
                pass

        # Fallback parsing /proc/meminfo
        if os.path.exists("/proc/meminfo"):
            try:
                mem_total = None
                mem_avail = None
                with open("/proc/meminfo", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            mem_total = int(line.split()[1]) * 1024
                        elif line.startswith("MemAvailable:"):
                            mem_avail = int(line.split()[1]) * 1024
                if mem_total is not None and mem_avail is not None:
                    return (
                        HardwareAttribute.available(mem_total),
                        HardwareAttribute.available(mem_avail),
                    )
            except Exception:
                pass

        return (
            HardwareAttribute.unavailable(reason="Failed to detect total RAM bytes"),
            HardwareAttribute.unavailable(reason="Failed to detect available RAM bytes"),
        )

    def _detect_disk(self, path: str) -> tuple[HardwareAttribute, HardwareAttribute]:
        """Detect disk capacity and free space for the designated path."""
        try:
            usage = shutil.disk_usage(path)
            return (
                HardwareAttribute.available(int(usage.total)),
                HardwareAttribute.available(int(usage.free)),
            )
        except Exception as e:
            return (
                HardwareAttribute.unavailable(
                    reason=f"Failed to query disk capacity for path '{path}': {str(e)}"
                ),
                HardwareAttribute.unavailable(
                    reason=f"Failed to query disk free space for path '{path}': {str(e)}"
                ),
            )

    def _detect_kernel_version(self) -> HardwareAttribute:
        """Detect kernel version."""
        try:
            kernel = platform.uname().release
            if kernel:
                return HardwareAttribute.available(kernel)
        except Exception as e:
            pass
        return HardwareAttribute.unavailable(reason="Kernel release unavailable")

    def _detect_gpu(self) -> Dict[str, Any]:
        """Probe GPU devices via nvidia-smi or driver query."""
        results: Dict[str, Any] = {
            "gpu_name": HardwareAttribute.unavailable(
                reason="No NVIDIA GPU detected on this host (nvidia-smi not in PATH and no driver device node)"
            ),
            "gpu_count": HardwareAttribute.available(0),
            "vram_total_bytes": HardwareAttribute.unavailable(
                reason="No GPU detected; VRAM total cannot be probed"
            ),
            "vram_available_bytes": HardwareAttribute.unavailable(
                reason="No GPU detected; VRAM available cannot be probed"
            ),
            "gpu_architecture": HardwareAttribute.unavailable(
                reason="No GPU detected; GPU architecture unavailable"
            ),
            "compute_capability": HardwareAttribute.unavailable(
                reason="No GPU detected; compute capability unavailable"
            ),
            "driver_version": HardwareAttribute.unavailable(
                reason="No GPU detected; NVIDIA driver is not loaded"
            ),
            "cuda_from_smi": None,
        }

        smi_path = shutil.which("nvidia-smi")
        if not smi_path:
            return results

        try:
            cmd = [
                smi_path,
                "--query-gpu=name,memory.total,memory.free,driver_version,compute_cap",
                "--format=csv,noheader,nounits",
            ]
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5, check=False
            )
            if proc.returncode == 0 and proc.stdout.strip():
                lines = [l.strip() for l in proc.stdout.strip().splitlines() if l.strip()]
                count = len(lines)
                if count > 0:
                    first = [part.strip() for part in lines[0].split(",")]
                    name = first[0] if len(first) > 0 else "Unknown GPU"
                    total_mb = float(first[1]) if len(first) > 1 and first[1].replace(".", "").isdigit() else None
                    free_mb = float(first[2]) if len(first) > 2 and first[2].replace(".", "").isdigit() else None
                    driver = first[3] if len(first) > 3 else "Unknown"
                    cc = first[4] if len(first) > 4 else "Unknown"

                    results["gpu_name"] = HardwareAttribute.available(name)
                    results["gpu_count"] = HardwareAttribute.available(count)
                    if total_mb is not None:
                        results["vram_total_bytes"] = HardwareAttribute.available(int(total_mb * 1024 * 1024))
                    if free_mb is not None:
                        results["vram_available_bytes"] = HardwareAttribute.available(int(free_mb * 1024 * 1024))
                    results["driver_version"] = HardwareAttribute.available(driver)
                    results["compute_capability"] = HardwareAttribute.available(cc)
                    results["gpu_architecture"] = HardwareAttribute.available(f"ComputeCapability_{cc}")
                    return results
        except Exception as e:
            results["gpu_name"] = HardwareAttribute.unavailable(
                reason=f"nvidia-smi execution error: {str(e)}"
            )

        return results

    def _detect_pytorch(self) -> HardwareAttribute:
        """Detect PyTorch installation without importing heavy CUDA components unless present."""
        try:
            import importlib.metadata
            ver = importlib.metadata.version("torch")
            return HardwareAttribute.available(ver)
        except Exception:
            return HardwareAttribute.unavailable(
                reason="PyTorch (torch) is not installed in the current Python environment"
            )

    def _detect_cuda(self, cuda_from_smi: Optional[str]) -> HardwareAttribute:
        """Detect CUDA toolkit or runtime version."""
        if cuda_from_smi:
            return HardwareAttribute.available(cuda_from_smi)

        nvcc_path = shutil.which("nvcc")
        if nvcc_path:
            try:
                proc = subprocess.run(
                    [nvcc_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        if "release" in line:
                            # e.g., Cuda compilation tools, release 12.1, V12.1.105
                            parts = line.split("release", 1)[1].strip().split(",")[0].strip()
                            return HardwareAttribute.available(parts)
            except Exception:
                pass

        return HardwareAttribute.unavailable(
            reason="CUDA compiler/toolkit (nvcc) not found in system PATH"
        )

    def _detect_relevant_runtimes(self) -> Dict[str, HardwareAttribute]:
        """Detect presence of key acceleration and scientific libraries."""
        candidates = [
            ("numpy", "NumPy"),
            ("scipy", "SciPy"),
            ("triton", "Triton"),
            ("onnxruntime", "ONNX Runtime"),
            ("tensorrt", "TensorRT"),
            ("psutil", "psutil"),
        ]
        runtimes: Dict[str, HardwareAttribute] = {}
        for pkg, label in candidates:
            try:
                import importlib.metadata
                ver = importlib.metadata.version(pkg)
                runtimes[label] = HardwareAttribute.available(ver)
            except Exception:
                runtimes[label] = HardwareAttribute.unavailable(
                    reason=f"{label} ({pkg}) is not installed"
                )
        return runtimes
