# Artifact Layout and Management

Every experiment maintains a strictly isolated directory inside `research/experiments/<experiment_id>/`.
No results or artifacts depend on files outside this folder.

```
research/experiments/EXP-000001/
├── config.json                 # Exact ExperimentConfig used
├── metadata.json               # Full ExperimentRecord compliant with schema
├── metrics.json                # Complete time, cpu, memory, gpu, disk telemetry
├── report.md                   # Human-readable markdown summary report
├── environment/
│   ├── hardware.json           # Machine hardware profile & fingerprint
│   └── software.json           # OS, kernel, python packages, git state
├── logs/
│   └── execution.log           # Full step-by-step timestamped execution trace
└── outputs/
    ├── output_manifest.json    # Manifest of generated tensors / images
    └── synthetic_feature_map.ppm # Raw generated payload
```

## Immutability & Integrity
- All output files are hashed with SHA-256 upon run completion.
- Checksums and file sizes are committed into `metadata.json` under `artifacts`.
- If an experiment fails, the directory and all partial artifacts remain completely intact.
