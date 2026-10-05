# Configuration System

The research harness enforces an architectural separation between:
1. **Experiment Configuration (`ExperimentConfig`)**
2. **Runtime Configuration (`RuntimeConfig`)**
3. **Environment Metadata (`EnvironmentMetadata`)**

---

## 1. Experiment Configuration (`ExperimentConfig`)
Specifies *what* scientific hypothesis is being evaluated.
Never contains host-specific paths, runner timeouts, or machine details.

```json
{
  "experiment_name": "baseline-matrix-determinism",
  "hypothesis": "Linear congruential pseudo-random matrix yields identical digests under seed 42.",
  "objective": "Establish baseline determinism.",
  "model_identifier": "synthetic-baseline-model-v0",
  "model_revision": "rev-phase0-001",
  "random_seed": 42,
  "workload_type": "synthetic_matrix",
  "workload_params": {
    "iterations": 2500,
    "matrix_size": 64
  },
  "tags": ["phase0", "baseline"],
  "notes": "Validation test"
}
```

---

## 2. Runtime Configuration (`RuntimeConfig`)
Specifies *how* the runner executes the workload on a given machine without changing scientific parameters.

```json
{
  "output_dir": "research/experiments",
  "timeout_seconds": 300.0,
  "sample_interval_ms": 50,
  "log_level": "INFO",
  "record_hardware": true,
  "record_software": true,
  "save_artifacts": true,
  "deterministic_mode": true
}
```

---

## 3. Environment Metadata
Autonomously recorded at runtime by the profiler.
Includes OS distro, kernel, Python packages, git commit, dirty tree status, and hardware profile. Stored in `environment/hardware.json` and `environment/software.json`.
