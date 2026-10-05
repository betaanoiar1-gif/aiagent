# Experiment Schema Specification

Every experiment record conforms strictly to the following unified schema:

## ExperimentRecord Fields

| Field Name | Type | Description | Mandatory |
| :--- | :--- | :--- | :--- |
| `experiment_id` | String | Unique sequential identifier (`EXP-000001`) | Yes |
| `experiment_name` | String | Human-readable experiment title | Yes |
| `hypothesis` | String | Scientific proposition being evaluated | Yes |
| `objective` | String | Target research objective | Yes |
| `timestamp` | String (ISO-8601) | Creation timestamp in UTC | Yes |
| `status` | String | `CREATED` \| `RUNNING` \| `COMPLETED` \| `FAILED` | Yes |
| `start_time` | Optional String | Workload execution start timestamp | No |
| `end_time` | Optional String | Workload execution termination timestamp | No |
| `duration_seconds` | Optional Float | Total elapsed wall-clock execution time | No |
| `git_commit` | String | SHA-1 commit hash of the codebase | Yes |
| `git_branch` | String | Active branch name | Yes |
| `git_is_dirty` | Boolean | Flag indicating uncommitted working tree changes | Yes |
| `hardware_fingerprint`| String | SHA-256 fingerprint of immutable hardware specs | Yes |
| `software_fingerprint`| String | SHA-256 fingerprint of software environment | Yes |
| `software_environment`| Object | Full dictionary snapshot of Python, OS, and packages | Yes |
| `hardware_profile` | Object | Full dictionary snapshot of host hardware specs | Yes |
| `model_identifier` | String | Model family or architecture identifier | Yes |
| `model_revision` | String | Specific model checkpoint or version | Yes |
| `random_seed` | Integer | Deterministic random seed | Yes |
| `input_reference` | Object | Dataset or prompt suite reference | Yes |
| `output_reference` | Object | Output format specifications and expectations | Yes |
| `configuration` | Object | Full snapshot of `ExperimentConfig` | Yes |
| `runtime_configuration`| Object| Snapshot of `RuntimeConfig` | Yes |
| `metrics` | Object | Resource and workload telemetry | Yes |
| `logs` | Object | Log file reference and line count | Yes |
| `artifacts` | Object | Catalog of all persistent files, sizes, and SHA-256 hashes | Yes |
| `decision` | String | `PENDING` \| `PASS` \| `FAIL` \| `INCONCLUSIVE` | Yes |
| `notes` | String | Experimental observations or replication trail | No |
| `failure_reason` | Optional String | Error description if status is `FAILED` | No |
| `stack_trace` | Optional String | Traceback trace if status is `FAILED` | No |

---

## Example `metadata.json` Snippet

```json
{
  "experiment_id": "EXP-000001",
  "experiment_name": "phase0-baseline-determinism-run1",
  "hypothesis": "A pseudo-random synthetic workload executed under seed 42 produces deterministic, bitwise reproducible artifacts across repeated runs.",
  "objective": "Establish baseline execution telemetry, resource monitoring benchmarks, and artifact layout for Phase 0 validation.",
  "status": "COMPLETED",
  "decision": "PASS",
  "duration_seconds": 0.01484,
  "git_commit": "52b32951531347b2c1000a85aa6b343e6f5578a4",
  "git_branch": "arena/32c43085-aiagent",
  "git_is_dirty": true,
  "hardware_fingerprint": "hwfp_10710551592e4e416e9ccab19449a7ac",
  "software_fingerprint": "swfp_7b538c3ae126068d119b028bc8cee39e",
  "random_seed": 42,
  "model_identifier": "synthetic-baseline-model-v0",
  "model_revision": "rev-phase0-001"
}
```
