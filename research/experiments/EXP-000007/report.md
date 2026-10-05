# Experiment Report: EXP-000007

**Experiment Name:** phase1b-gpu-baseline-recovery-audit  
**Status:** `FAILED`  
**Scientific Decision:** `FAIL`  
**Timestamp (Created):** 2026-10-05T20:39:07.459776+00:00  
**Start Time:** 2026-10-05T20:39:07.460633+00:00  
**End Time:** 2026-10-05T20:39:07.473854+00:00  
**Duration:** 0.0119 s  

---

## 1. Scientific Context

- **Hypothesis:** Determine whether physical GPU hardware accelerator and CUDA runtime can be discovered on host for Phase 1B baseline recovery.
- **Objective:** Empirically evaluate Decision Gate (Path A vs Path B) for Phase 1B real GPU baseline execution.
- **Model Identifier:** `Wan-AI/Wan2.1-T2V-1.3B`
- **Model Revision:** `main`
- **Random Seed:** `42`

---

## 2. Environment & Traceability

- **Git Commit:** `52b32951531347b2c1000a85aa6b343e6f5578a4` (Dirty: `True`)
- **Git Branch:** `arena/32c43085-aiagent`
- **Hardware Fingerprint:** `hwfp_10710551592e4e416e9ccab19449a7ac`
- **Software Fingerprint:** `swfp_7b538c3ae126068d119b028bc8cee39e`
- **OS:** Debian GNU/Linux 12 (bookworm)
- **Kernel:** 6.1.158+
- **Python Version:** 3.11.2

### Hardware Profile Summary

- **CPU Model:** Intel(R) Xeon(R) Processor @ 2.60GHz
- **CPU Cores:** 1 physical / 2 logical
- **RAM Total:** 3.85 GB
- **GPU Device:** None (Status: `unavailable`, Reason: No NVIDIA GPU detected on this host (nvidia-smi not in PATH and no driver device node))
- **CUDA Version:** N/A (Status: `unavailable`)
- **PyTorch Version:** N/A (Status: `unavailable`)

---

## 3. Experiment Configuration

```json
{
  "experiment_name": "phase1b-gpu-baseline-recovery-audit",
  "hypothesis": "Determine whether physical GPU hardware accelerator and CUDA runtime can be discovered on host for Phase 1B baseline recovery.",
  "objective": "Empirically evaluate Decision Gate (Path A vs Path B) for Phase 1B real GPU baseline execution.",
  "model_identifier": "Wan-AI/Wan2.1-T2V-1.3B",
  "model_revision": "main",
  "random_seed": 42,
  "workload_type": "hardware_recovery_audit",
  "workload_params": {
    "model_identifier": "Wan-AI/Wan2.1-T2V-1.3B",
    "phase": "1B",
    "prompt_id": "V01"
  },
  "input_reference": {},
  "output_reference": {},
  "tags": [
    "phase1b",
    "hardware_recovery",
    "decision_gate"
  ],
  "notes": "Phase 1B empirical decision gate execution.",
  "experiment_id": null
}
```

---

## 4. Resource & Execution Telemetry

### Timing Telemetry
- **Total Wall-Clock Time:** 0.01172 s
- **Measurement Harness Overhead:** 0.000699 s

### Compute & Memory Telemetry
- **CPU Mean Utilization:** 0.0%
- **CPU Peak Utilization:** 0.0%
- **User CPU Time:** 0.0 s
- **System CPU Time:** 0.0 s
- **Start RSS Memory:** 21.82 MB
- **Peak RSS Memory:** 21.82 MB
- **End RSS Memory:** 21.91 MB
- **Delta RSS Memory:** 0.09 MB

### Accelerator (GPU/VRAM) Telemetry
- **Status:** `unavailable`
- **Reason:** nvidia-smi not found; accelerator telemetry unavailable on this host
- **Peak VRAM:** None

### Storage & Artifacts Footprint
- **Artifacts Size:** 14042 bytes
- **Disk Free Delta:** 0 bytes

### Workload Specific Outputs
- **Iterations Completed:** N/A
- **Output Digest (SHA-256):** `N/A`

---

## 5. Artifacts & Outputs

No persistent artifacts recorded.

---

## 6. Logs & Diagnostics

- **Log File:** `logs/execution.log`
- **Log Lines Count:** 20

---

## 7. Failure Analysis & Diagnostics

**Failure Reason:** EnvironmentHardwarePrerequisiteError: Host environment cannot execute baseline model 'Wan-AI/Wan2.1-T2V-1.3B'. Discovered Deficiencies: [Missing physical GPU: detected 0 GPUs, minimum required is 1. | CUDA compiler/runtime unavailable: CUDA compiler/toolkit (nvcc) not found in system PATH. | Insufficient host system RAM: detected 3.85 GB, minimum required is 16.0 GB.]. Per Phase 1 research protocol, CPU-only generation is prohibited because it cannot measure VRAM or GPU compute profile. Execution aborted to preserve empirical validity.

**Stack Trace:**
```text
Traceback (most recent call last):
  File "/home/user/aiagent/runtime/runner/runner.py", line 164, in run
    workload_res = active_engine.execute(
                   ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/aiagent/engines/baseline_engine.py", line 101, in execute
    raise EnvironmentHardwarePrerequisiteError(
engines.baseline_engine.EnvironmentHardwarePrerequisiteError: EnvironmentHardwarePrerequisiteError: Host environment cannot execute baseline model 'Wan-AI/Wan2.1-T2V-1.3B'. Discovered Deficiencies: [Missing physical GPU: detected 0 GPUs, minimum required is 1. | CUDA compiler/runtime unavailable: CUDA compiler/toolkit (nvcc) not found in system PATH. | Insufficient host system RAM: detected 3.85 GB, minimum required is 16.0 GB.]. Per Phase 1 research protocol, CPU-only generation is prohibited because it cannot measure VRAM or GPU compute profile. Execution aborted to preserve empirical validity.

```

---

## 8. Notes & Conclusions

Phase 1B empirical decision gate execution.
