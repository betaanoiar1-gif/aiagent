# Hardware Profiler & Fingerprinting

## 1. Principles
- **No Fabrications**: Under no circumstances will the profiler guess, fabricate, or mock hardware capability values.
- **Explicit Unavailability**: If a feature is absent (e.g. no GPU device node or NVIDIA driver), the profiler returns:
  ```json
  {
    "value": null,
    "status": "unavailable",
    "reason": "No NVIDIA GPU detected on this host (nvidia-smi not in PATH and no driver device node)"
  }
  ```

---

## 2. Discovered Attributes
- **GPU Attributes**:
  - `gpu_name`
  - `gpu_count`
  - `vram_total_bytes`
  - `vram_available_bytes`
  - `gpu_architecture`
  - `compute_capability`
  - `driver_version`
  - `cuda_version`
- **CPU Attributes**:
  - `cpu_model` (extracted from `/proc/cpuinfo` or `platform.processor()`)
  - `cpu_cores_physical`
  - `cpu_cores_logical`
- **Memory & Storage**:
  - `ram_total_bytes`
  - `ram_available_bytes`
  - `disk_capacity_bytes`
  - `disk_free_bytes`
- **Host & Runtime**:
  - `os_name`
  - `os_release`
  - `kernel_version`
  - `host_architecture`
  - `python_version`
  - `pytorch_version`
  - `relevant_runtimes` (NumPy, SciPy, Triton, ONNX Runtime, TensorRT, psutil)

---

## 3. Deterministic Hardware Fingerprint Algorithm
The hardware fingerprint is derived by computing the SHA-256 digest of immutable hardware parameters:

$$\text{String} = \text{cpu\_model} \parallel \text{phys\_cores} \parallel \text{log\_cores} \parallel \text{ram\_total} \parallel \text{host\_arch} \parallel \text{gpu\_name} \parallel \text{gpu\_count} \parallel \text{gpu\_arch}$$

$$\text{hwfp} = \text{"hwfp\_"} + \text{SHA-256}(\text{String})[0:32]$$

This ensures that repeated executions on the exact same physical or virtual hardware node produce identical fingerprints, enabling reliable hardware tracking across research trials.
