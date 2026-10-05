# Quickstart Guide

## 1. Inspect Hardware Profile & Fingerprint
To view host hardware capabilities:
```bash
python3 scripts/profile_hardware.py
```
Or view JSON representation:
```bash
python3 scripts/profile_hardware.py --json
```

---

## 2. Run a New Experiment
Run an experiment with custom parameters:
```bash
python3 scripts/run_experiment.py \
  --name "custom-experiment-run" \
  --hypothesis "Testing throughput at matrix size 64" \
  --seed 42 \
  --iterations 2500 \
  --matrix-size 64
```
Or launch using a predefined JSON config file:
```bash
python3 scripts/run_experiment.py --config research/benchmarks/synthetic_matrix_benchmark.json
```

---

## 3. Reproduce an Existing Experiment
To reproduce an experiment by its ID:
```bash
python3 scripts/rerun_experiment.py EXP-000001
```
This loads `EXP-000001/config.json`, executes a new replica experiment, compares output hashes and telemetry, and generates a comparative markdown report in `research/reports/`.

---

## 4. Compare Two Experiments
Compare any two experiment records in the registry:
```bash
python3 scripts/compare_experiments.py EXP-000001 EXP-000002 --markdown
```

---

## 5. View or Regenerate an Experiment Report
Display the formatted markdown report:
```bash
python3 scripts/generate_report.py EXP-000001
```

---

## 6. Run the Validation Test Suite
Execute all automated validation tests:
```bash
python3 -m pytest -v tests/
```
