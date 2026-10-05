# Experiment Report: EXP-000003

**Experiment Name:** phase0-fault-tolerance-verification  
**Status:** `FAILED`  
**Scientific Decision:** `FAIL`  
**Timestamp (Created):** 2026-10-05T20:10:38.822477+00:00  
**Start Time:** 2026-10-05T20:10:38.824969+00:00  
**End Time:** 2026-10-05T20:10:38.840173+00:00  
**Duration:** 0.0115 s  

---

## 1. Scientific Context

- **Hypothesis:** The research harness preserves full failure diagnostics, execution logs, and environment metadata without data loss upon workload abort.
- **Objective:** Verify fault tolerance, state transition to FAILED, error capture, and stack trace persistence.
- **Model Identifier:** `synthetic-baseline-model-v0`
- **Model Revision:** `rev-phase0-001`
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
  "experiment_name": "phase0-fault-tolerance-verification",
  "hypothesis": "The research harness preserves full failure diagnostics, execution logs, and environment metadata without data loss upon workload abort.",
  "objective": "Verify fault tolerance, state transition to FAILED, error capture, and stack trace persistence.",
  "model_identifier": "synthetic-baseline-model-v0",
  "model_revision": "rev-phase0-001",
  "random_seed": 42,
  "workload_type": "synthetic_matrix",
  "workload_params": {
    "simulate_failure": true,
    "failure_step": 128,
    "failure_message": "Host out of memory simulation during tensor matrix multiplication"
  },
  "input_reference": {},
  "output_reference": {},
  "tags": [
    "phase0",
    "fault_tolerance",
    "lifecycle_failure"
  ],
  "notes": "Validation trial for failure handling and error diagnostics.",
  "experiment_id": null
}
```

---

## 4. Resource & Execution Telemetry

### Timing Telemetry
- **Total Wall-Clock Time:** 0.011039 s
- **Measurement Harness Overhead:** 0.001812 s

### Compute & Memory Telemetry
- **CPU Mean Utilization:** 0.0%
- **CPU Peak Utilization:** 0.0%
- **User CPU Time:** 0.0 s
- **System CPU Time:** 0.0 s
- **Start RSS Memory:** 22.21 MB
- **Peak RSS Memory:** 22.21 MB
- **End RSS Memory:** 22.21 MB
- **Delta RSS Memory:** 0.0 MB

### Accelerator (GPU/VRAM) Telemetry
- **Status:** `unavailable`
- **Reason:** nvidia-smi not found; accelerator telemetry unavailable on this host
- **Peak VRAM:** None

### Storage & Artifacts Footprint
- **Artifacts Size:** 14028 bytes
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

**Failure Reason:** EngineExecutionFailure: Host out of memory simulation during tensor matrix multiplication

**Stack Trace:**
```text
Traceback (most recent call last):
  File "/home/user/aiagent/runtime/runner/runner.py", line 164, in run
    workload_res = active_engine.execute(
                   ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/aiagent/engines/mock_engine.py", line 49, in execute
    raise RuntimeError(f"EngineExecutionFailure: {error_msg}")
RuntimeError: EngineExecutionFailure: Host out of memory simulation during tensor matrix multiplication

```

---

## 8. Notes & Conclusions

Validation trial for failure handling and error diagnostics.
