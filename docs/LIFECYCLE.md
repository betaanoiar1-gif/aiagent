# Experiment Lifecycle

Every experiment managed by the research harness transitions through a strictly defined finite state machine:

```
                  +-------------+
                  |   CREATED   |
                  +-------------+
                         |
                         v
                  +-------------+
                  |   RUNNING   |
                  +-------------+
                   /           \
     Workload Success         Workload Error / Abort
                 /               \
                v                 v
        +-------------+     +-------------+
        |  COMPLETED  |     |   FAILED    |
        +-------------+     +-------------+
```

---

## State Definitions

### 1. CREATED
- **Trigger**: `runner.run(config)` begins.
- **Operations**:
  - Unique `experiment_id` allocated (e.g. `EXP-000001`).
  - Experiment directory tree provisioned (`logs/`, `outputs/`, `environment/`).
  - Isolated file logger attached to `<exp_dir>/logs/execution.log`.
  - Hardware and software discovery runs; snapshots saved to `environment/hardware.json` and `environment/software.json`.
  - Pure experiment configuration serialized to `config.json`.
  - Initial `ExperimentRecord` committed to registry with `status = CREATED`.

### 2. RUNNING
- **Trigger**: Resource monitor initialization.
- **Operations**:
  - `start_time` recorded in ISO-8601 UTC.
  - Background `ResourceMonitor` thread launched.
  - Model weights / definitions loaded.
  - Workload executed.
  - Live progress and debug traces written to `execution.log`.

### 3. COMPLETED
- **Trigger**: Successful workload completion without unhandled exceptions.
- **Operations**:
  - `end_time` recorded and `duration_seconds` calculated.
  - `ResourceMonitor` stopped; telemetry compiled into `metrics.json`.
  - Output files cataloged in `outputs/` and hashes computed.
  - `report.md` generated summarizing all telemetry and environment specs.
  - Final record updated with `status = COMPLETED` and `decision = PASS`.
  - Registry index updated.

### 4. FAILED (Zero Data Loss)
- **Trigger**: Workload exception, timeout, OOM, or unhandled runtime error.
- **Operations**:
  - Exception caught; `failure_reason` and full traceback `stack_trace` recorded.
  - `end_time` and partial `duration_seconds` calculated.
  - `ResourceMonitor` safely stopped; partial metrics persisted.
  - Engine teardown invoked.
  - `logs/execution.log` flushed with critical error details.
  - `report.md` generated with dedicated **Failure Analysis & Diagnostics** section.
  - Final record persisted with `status = FAILED` and `decision = FAIL`.
  - No directory or file is ever deleted upon failure. Complete forensic evidence is preserved.
