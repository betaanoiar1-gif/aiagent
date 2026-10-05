# Experiment Comparison: `EXP-000001` vs `EXP-000002`

**Reproducibility Verdict:** `CONFIG_MISMATCH`  
**Bitwise Identical Output:** `False`  
**Hardware Match:** `True`  
**Software Match:** `True`  

---

## 1. Parity Matrix

| Dimension | Experiment 1 (`EXP-000001`) | Experiment 2 (`EXP-000002`) | Match? |
| :--- | :--- | :--- | :--- |
| Random Seed | `123` | `999999` | `False` |
| Configuration | - | - | `False` |
| Hardware Fingerprint | - | - | `True` |
| Software Fingerprint | - | - | `True` |
| Output Checksum Match | - | - | `False` |

---

## 2. Resource Variance & Natural Jitter

| Metric | EXP-000001 | EXP-000002 | Delta | % Delta |
| :--- | :--- | :--- | :--- | :--- |
| Wall-Clock Time (s) | 0.0125 | 0.0117 | -0.0008 | -6.11% |
| CPU Mean (%) | 2231.7 | 0.0 | -2231.7 | -100.0% |
| Peak RSS (MB) | 32.43 | 32.43 | +0.00 | +0.00% |

---

## 3. Findings & Scientific Analysis

- Random seeds differ; deterministic identical outputs not expected.
- Configurations differ between experiments.
