# Known Limitations & Phase 0 Boundaries

In strict compliance with the **PHASE 0 RULES**, the current implementation enforces the following boundaries:

## 1. Physical Hardware Limitations
- **No Physical GPU in Current Host**: The current virtualized sandbox environment lacks a physical NVIDIA GPU (`nvidia-smi` and CUDA device nodes are absent). The profiler accurately records GPU and CUDA status as `unavailable`. Full GPU profiling and VRAM telemetry hooks are implemented, ready for hosts equipped with NVIDIA accelerators.
- **PyTorch Absence**: PyTorch is not currently installed in the global environment; its version is reported accurately as `status: unavailable`.

## 2. Workload Scope
- **Synthetic Workloads Only**: In Phase 0, workloads are intentionally restricted to deterministic mathematical synthetic computations to prove infrastructure correctness. No actual image/video diffusion models (e.g., Stable Diffusion, Flux, Wan, CogVideo) are executed.

## 3. Strict Prohibitions Enforced
- No model training, fine-tuning, or checkpoint weights modification.
- No model quantization, pruning, distillation, or sparse attention kernels.
- No inference optimizations, caching, or model routing.
- No web UI, authentication, or deployment infrastructure.
- Zero claims of research novelty.

All model optimizations and generative baseline trials are strictly reserved for Phase 1 and subsequent phases once Phase 0 infrastructure is accepted.
