# AI Research Laboratory — Phase 0 Foundation

A scientifically rigorous, fully reproducible research foundation engineered to support long-term generative AI research (image and video generation with minimal compute, VRAM, and RAM).

> **Status:** PHASE 0 ONLY. No model optimization, fine-tuning, web UI, or Phase 1 features are included.

---

## Core Capabilities
- **Hardware & Software Profiling**: Automatic hardware discovery, CPU/RAM/GPU detection, zero-fabrication reporting, and deterministic hardware fingerprinting (`hwfp_*`).
- **Centralized Experiment Registry**: Persistent index and isolated directory structure for every experiment (`EXP-xxxxxx`).
- **Complete Experiment Lifecycle**: Explicit `CREATED` -> `RUNNING` -> `COMPLETED` / `FAILED` states with zero data loss on failure.
- **Resource Measurement**: Sub-millisecond overhead telemetry capturing wall-clock time, CPU utilization, peak RSS memory, disk deltas, and accelerator states.
- **Strict Reproducibility**: Automated re-execution engine comparing configuration parity, bitwise identical output checksums, and natural OS scheduling jitter.
- **Automated Validation**: 26 automated unit and integration tests covering profilers, lifecycle, runners, failure handling, and reproducibility.

---

## Repository Layout
- `research/`: Formal hypotheses (`hypotheses/`), experiments (`experiments/`), benchmarks (`benchmarks/`), reports (`reports/`), datasets (`datasets/`), and prompts (`prompts/`).
- `runtime/`: Core execution harness, hardware/software profiler, concurrent resource monitor, runner, and configuration schemas.
- `engines/`: Base compute engine interface and deterministic synthetic benchmark engine.
- `models/`: Base model wrapper and synthetic benchmark model.
- `evaluation/`: Report generator, differential comparison engine, and metric validator.
- `docs/`: In-depth architecture, lifecycle, schema, hardware profiler, configuration, and reproducibility documentation.
- `tests/`: Comprehensive automated pytest suite.
- `scripts/`: Production-ready CLI utilities for running, reproducing, comparing, and profiling experiments.

---

## Quickstart

### Run Tests
```bash
python3 -m pytest -v tests/
```

### Inspect Hardware Profile
```bash
python3 scripts/profile_hardware.py
```

### Run an Experiment
```bash
python3 scripts/run_experiment.py --name "baseline-run" --seed 42 --iterations 2500
```

### Reproduce an Experiment
```bash
python3 scripts/rerun_experiment.py EXP-000001
```

### Compare Experiments
```bash
python3 scripts/compare_experiments.py EXP-000001 EXP-000002 --markdown
```

For complete documentation, see the [docs/](docs/) directory and [PHASE_0_REPORT.md](PHASE_0_REPORT.md).
