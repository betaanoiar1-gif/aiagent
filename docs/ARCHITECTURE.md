# Research Laboratory Architecture

## 1. Architectural Philosophy
The research harness is engineered according to the following foundational principles:

1. **Strict Decoupling of Concerns**:
   - Scientific specifications (`ExperimentConfig`) are isolated from runtime execution settings (`RuntimeConfig`) and host telemetry (`HardwareProfile`, `SoftwareProfile`).
2. **Absolute Empirical Truth (Zero Fabrication)**:
   - When a hardware capability (such as an NVIDIA GPU, CUDA compiler, or driver) is absent, the system explicitly reports `status: unavailable` with the physical cause. No metrics or synthetic devices are ever invented.
3. **Bitwise Reproducibility Verification**:
   - Experiments track complete cryptographic hashes of configurations, environment snapshots, random seeds, and generated output artifacts.
4. **Fault Resilience & Zero Data Loss**:
   - Workload exceptions, process crashes, or out-of-memory errors transition the experiment lifecycle to `FAILED`, preserving full stack traces, partial execution logs, environment profiles, and metrics without discarding the experiment folder.
5. **Minimal Measurement Overhead**:
   - The measurement harness operates concurrently using background sampling threads, incurring less than 1 ms of measurement overhead, ensuring it does not distort execution profiles.

---

## 2. System Layers

```
+-------------------------------------------------------------------+
|                        RESEARCH INTERFACE                         |
|   scripts/ (CLI Tools: run, rerun, compare, profile, report)      |
+-------------------------------------------------------------------+
                                 |
                                 v
+-------------------------------------------------------------------+
|                       BENCHMARK RUNNER LAYER                      |
|   runtime/runner/runner.py, reproducibility.py                   |
+-------------------------------------------------------------------+
           |                             |                   |
           v                             v                   v
+-----------------------+   +-----------------------+   +-----------+
|    PROFILING LAYER    |   |   MEASUREMENT LAYER   |   | REGISTRY  |
| hardware.py           |   | monitor.py            |   | registry  |
| software.py           |   | metrics.py            |   | .py       |
+-----------------------+   +-----------------------+   +-----------+
           |                             |                   |
           +-----------------------------+-------------------+
                                 |
                                 v
+-------------------------------------------------------------------+
|                     ENGINE & MODEL ABSTRACTIONS                   |
|   engines/ (BaseEngine, DeterministicSyntheticEngine)             |
|   models/  (BaseModel, SyntheticBenchmarkModel)                   |
+-------------------------------------------------------------------+
                                 |
                                 v
+-------------------------------------------------------------------+
|                     EVALUATION & REPORTING                        |
|   evaluation/ (reporter.py, comparison.py, metrics.py)            |
+-------------------------------------------------------------------+
```

---

## 3. Component Interactions
1. **Runner Invocation**: `BenchmarkRunner` receives `ExperimentConfig` and `RuntimeConfig`.
2. **Environment Capture**: `HardwareProfiler` and `SoftwareProfiler` generate deterministic fingerprints (`hwfp_*`, `swfp_*`).
3. **Artifact Initialization**: The experiment directory is provisioned in `research/experiments/<exp_id>/` and `status` is set to `CREATED`.
4. **Active Monitoring**: `ResourceMonitor` starts background sampling of CPU RSS and usage.
5. **Execution**: Engine runs the workload seeded deterministically.
6. **Telemetry Harvest**: `ResourceMonitor` stops, telemetry is aggregated into `metrics.json`.
7. **Artifact Integrity**: Output files are cataloged with SHA-256 hashes.
8. **Finalization**: `ExperimentReporter` emits `report.md`, and record is committed to `registry.json` as `COMPLETED` (or `FAILED` upon exception).
