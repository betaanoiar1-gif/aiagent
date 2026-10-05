# Experiment Comparison: `EXP-000001` vs `EXP-000002`

**Reproducibility Verdict:** `DETERMINISTIC_MATCH`  
**Bitwise Identical Output:** `True`  
**Hardware Match:** `True`  
**Software Match:** `True`  

---

## 1. Parity Matrix

| Dimension | Experiment 1 (`EXP-000001`) | Experiment 2 (`EXP-000002`) | Match? |
| :--- | :--- | :--- | :--- |
| Random Seed | `42` | `42` | `True` |
| Configuration | - | - | `True` |
| Hardware Fingerprint | - | - | `True` |
| Software Fingerprint | - | - | `True` |
| Output Checksum Match | - | - | `True` |

---

## 2. Resource Variance & Natural Jitter

| Metric | EXP-000001 | EXP-000002 | Delta | % Delta |
| :--- | :--- | :--- | :--- | :--- |
| Wall-Clock Time (s) | 0.0148 | 0.0164 | +0.0015 | +10.34% |
| CPU Mean (%) | 0.0 | 0.0 | +0.0 | +0.0% |
| Peak RSS (MB) | 21.82 | 22.21 | +0.40 | +1.83% |

---

## 3. Findings & Scientific Analysis

- Workload output hashes are bitwise identical (34705c110a83d134144b4d48c8b50de073926423136ea173bfe1ae903da80ef2). Observed natural wall-clock variance of +0.0015s (+10.34%) and peak memory delta of +0.40MB due to OS thread scheduling and paging.
- Scientific reproducibility confirmed: mathematical outputs are bitwise identical.
