#!/usr/bin/env python3
"""CLI utility to inspect host hardware profile and deterministic fingerprint."""

import argparse
import sys
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from runtime.profiler.hardware import HardwareProfiler


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile host hardware specifications.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON format.")
    args = parser.parse_args()

    profiler = HardwareProfiler()
    profile = profiler.profile()

    if args.json:
        print(profile.to_json(indent=2))
        return

    print("=" * 60)
    print(" RESEARCH HARNESS — HARDWARE PROFILE")
    print("=" * 60)
    print(f"Hardware Fingerprint : {profile.hardware_fingerprint}")
    print(f"Host Architecture    : {profile.host_architecture.value}")
    print(f"OS / Kernel          : {profile.os_name.value} {profile.os_release.value} ({profile.kernel_version.value})")
    print(f"CPU Model            : {profile.cpu_model.value}")
    print(f"CPU Physical Cores   : {profile.cpu_cores_physical.value}")
    print(f"CPU Logical Cores    : {profile.cpu_cores_logical.value}")
    ram_gb = (
        round(profile.ram_total_bytes.value / (1024**3), 2)
        if profile.ram_total_bytes.value
        else "N/A"
    )
    print(f"RAM Total            : {ram_gb} GB")
    gpu_val = profile.gpu_name.value
    if profile.gpu_name.status == "available":
        print(f"GPU Accelerator      : {gpu_val} (Count: {profile.gpu_count.value})")
    else:
        print(f"GPU Accelerator      : None (status='unavailable', reason='{profile.gpu_name.reason}')")

    print(f"CUDA Version         : {profile.cuda_version.value} (status='{profile.cuda_version.status}')")
    print(f"PyTorch Version      : {profile.pytorch_version.value} (status='{profile.pytorch_version.status}')")
    print(f"Python Version       : {profile.python_version.value}")
    print("=" * 60)


if __name__ == "__main__":
    main()
