# PHASE 1 EXPERIMENTAL ROADMAP: LOW-COMPUTE GENERATIVE RUNTIME (LCGR)
## Progressive Empirical Roadmap from Toy Mathematical Simulation to Foundation Generative Models

> **Notice:** This document defines the formal experimental verification protocol to be executed in subsequent phases. In strict accordance with Phase 1 directives, these experiments are specified mathematically and procedurally, but are **NOT** executed during this theoretical phase.

---

## Roadmap Architecture
The roadmap is structured in five strictly gated tiers of increasing complexity:

```
[Experiment A: Toy Math Simulator]
       │ (Pure 2D grid matrix simulation, zero neural weights, runs in <10s on CPU)
       ▼
[Experiment B: Synthetic Image Generation]
       │ (Toy diffusion/flow matching on synthetic geometric shapes / MNIST)
       ▼
[Experiment C: Small Real Image Model]
       │ (Stable Diffusion v1.5 with patch-selective attention & Semantic Compute Field)
       ▼
[Experiment D: Small Video Model]
       │ (Moving MNIST / Synthetic Sprites / Toy Temporal DiT with Temporal Deltas)
       ▼
[Experiment E: Full Foundation Generative Video Model]
         (Wan2.1-T2V-1.3B / LTX-Video-2B with full LCGR compiler & World State)
```

---

## 1. Experiment A: Toy Mathematical Simulator

### 1.1 Objective
Empirically validate the mathematical convergence of the **Semantic Compute Field (SCF)** and the **Marginal Value of Computation (MVC)** stopping policy in an idealized, fully controlled matrix simulation without the confounding complexity of deep neural networks.

### 1.2 System Implementation
- A 2D scalar field $Z \in \mathbb{R}^{64 \times 64}$ initialized with high-frequency Gaussian noise.
- A synthetic target field $Z^* \in \mathbb{R}^{64 \times 64}$ with structured geometric regions (high-importance circular focal zone, low-importance uniform background).
- An iterative relaxation operator simulating reverse diffusion:
  $$Z_{s+1}(i, j) = Z_s(i, j) - \eta \cdot \nabla \mathcal{L}(Z_s(i, j), Z^*(i, j)) + \sigma_s \mathcal{N}(0, 1)$$
- The LCGR controller evaluates $\mathcal{C}(i, j)$ and dynamically masks cell updates based on local error $\mathcal{E}_s(i, j)$ and stopping condition $\text{MVC}_s(i, j) < \kappa$.

### 1.3 Variables
- **Independent Variables:**
  - Compute Allocation Policy: Uniform (100% cells updated every step) vs. Random vs. Semantic Compute Field (SCF).
  - Termination Threshold $\kappa \in [10^{-4}, 10^{-1}]$.
  - Semantic Importance weighting ratio $\omega_{\text{focal}} / \omega_{\text{background}} \in [1.0, 10.0]$.
- **Dependent Variables:**
  - Total Cell Update Operations (Simulated FLOPs).
  - Root Mean Squared Error (RMSE) on Focal Region vs Background.
  - Number of Iterations to Convergence.
  - Controller Scheduling Overhead (CPU clock cycles).

### 1.4 Baseline & Comparative Anchor
- **Baseline:** Fixed 50-step uniform grid relaxation where all $64 \times 64 = 4096$ cells are updated on every step ($4096 \times 50 = 204,800$ updates).

### 1.5 Success & Failure Criteria
- **Success Criteria:**
  - SCF achieves $\text{RMSE}_{\text{focal}} \le \text{RMSE}_{\text{baseline}}$ using $\le 50\%$ total cell updates ($\le 102,400$ updates).
  - Stop condition cleanly terminates background cell computation by step 15 while continuing focal refinement.
  - Controller scheduling overhead accounts for $< 3\%$ of total execution time.
- **Failure Criteria:**
  - Non-uniform update causes edge ringing artifacts along the boundary between focal and background zones.
  - Greedy stopping causes premature convergence with error exceeding baseline by $>10\%$.

---

## 2. Experiment B: Synthetic Image Generation (Toy Diffusion)

### 2.1 Objective
Validate dynamic token pruning and error-driven selective refinement on a lightweight, trainable generative diffusion model (e.g. 2-layer ConvNet or tiny Vision Transformer on $32 \times 32$ synthetic geometric shapes or MNIST/CIFAR).

### 2.2 System Implementation
- A miniature Diffusion Transformer (Tiny-DiT: 4 layers, 128 hidden dim, 4 heads, ~800k parameters).
- Trained to synthesize multi-object scenes (e.g. distinct colored geometric polygons on textured backgrounds).
- LCGR patch token mask $\mathbf{M}_{i,j}^{(s)}$ selectively deactivates background tokens in layers 3–4 during denoising steps $s > 10$.

### 2.3 Variables
- **Independent Variables:**
  - Token Sparsity Policy: Dense Baseline vs. Random Dropout vs. Saliency-Gated Pruning via $\mathcal{C}(x,y)$.
  - Saliency Threshold $\tau_{\text{compute}} \in [0.1, 0.9]$.
- **Dependent Variables:**
  - Active Token-Layer FLOPs per sample.
  - Fr閏het Inception Distance (FID) on synthetic test set.
  - Boundary Stitching Error across patch perimeters.
  - Peak Memory footprint during attention computation.

### 2.4 Baseline
- Dense Tiny-DiT processing 100% of spatial tokens across all 4 layers and 30 denoising steps.

### 2.5 Success & Failure Criteria
- **Success Criteria:**
  - $\ge 40\%$ reduction in active attention FLOPs.
  - Synthetic FID degradation $\le 5\%$ relative to dense baseline.
  - Clean spatial integration without visible tile seams.
- **Failure Criteria:**
  - Spatial discontinuity artifacts along pruned patch boundaries.
  - Controller instability where token masks oscillate chaotically between consecutive steps.

---

## 3. Experiment C: Small Real Image Model (Stable Diffusion v1.5)

### 3.1 Objective
Apply the Semantic Compute Field and progressive refinement planning to an un-optimized production foundation model (**Stable Diffusion v1.5**, 1.07B parameters) using the standardized Phase 1 prompt dataset (`PROMPT-SUITE-V1`).

### 3.2 System Implementation
- Unmodified pre-trained SD v1.5 weights (`v1-5-pruned-emaonly.safetensors`).
- LCGR Semantic Parser extracts subject masks from text prompt cross-attention maps at step 3.
- Spatial-selective denoising: U-Net self-attention layers apply a dynamic spatial mask, skipping cross-attention and feed-forward updates on non-salient background tokens during steps 15–50.
- Progressive intelligence ladder: $L_1$ (5-step draft preview) $\rightarrow L_2$ (adaptive selective 25-step) $\rightarrow L_3$ (full 50-step focal refinement).

### 3.3 Variables
- **Independent Variables:**
  - Prompt Class: Simple object (I01), Human anatomy (I03), Architecture (I05), Complex scene (I07).
  - Target Quality Contract $Q_{\text{target}} \in [0.7, 1.0]$.
  - Spatial Saliency Threshold.
- **Dependent Variables:**
  - Total TFLOPs per image generation.
  - Wall-clock inference latency on target GPU (e.g. RTX 3090 / 4090).
  - Peak VRAM during U-Net execution.
  - CLIP Score (ViT-L/14) and LPIPS distance to 50-step dense baseline.
  - Hand anatomical defect rate on I03.

### 3.4 Baseline
- Standard unconditional SD v1.5 pipeline: 50 steps DDIM / 25 steps Euler, full dense attention over all $64 \times 64 = 4096$ latent tokens.

### 3.5 Success & Failure Criteria
- **Success Criteria:**
  - Total latency and FLOPs reduced by $\ge 35\%$ on average across 10 prompts.
  - CLIP alignment score within $0.5$ points of dense baseline ($>30.5$ on I01–I10).
  - Zero degradation on high-saliency features (face and hand geometry preserved).
  - Peak VRAM reduced by $\ge 25\%$ during selective steps.
- **Failure Criteria:**
  - Blurring, haloing, or texture mismatch around subject boundaries.
  - Kernel launch overhead on sparse masks negates wall-clock speedups.

---

## 4. Experiment D: Small Video Model (Temporal Delta Synthesis)

### 4.1 Objective
Empirically test **Temporal Delta Generation (TDG)** and error drift bounding on a small-scale video model (e.g., Moving MNIST, Toy Video DiT, or SVDK 16-frame 256x256).

### 4.2 System Implementation
- Keyframe $t_0$ generated fully.
- Frames $t \in [1, 15]$ synthesized using motion-compensated latent warping:
  $$\mathbf{z}_{t+1} = \mathcal{W}(\mathbf{z}_t, \mathbf{v}_t) + \mathbf{M}_{\text{innovation}} \odot \Delta \mathbf{z}_{t+1}$$
- Optical flow $\mathbf{v}_t$ predicted by lightweight spatial-temporal guidance head.
- Accumulation monitor checks drift $\mathcal{D}(t)$; triggers anchor keyframe when $\mathcal{D}(t) > \tau_{\text{drift}}$.

### 4.3 Variables
- **Independent Variables:**
  - Delta Generation Mode: Dense independent generation vs. Flow-Warped Delta vs. Delta + Residual Correction.
  - Keyframe Anchor Interval: Fixed ($K=4, 8, 16$) vs. Adaptive Drift-Triggered.
  - Motion Magnitude (slow camera drift vs. high-velocity object motion).
- **Dependent Variables:**
  - Wall-clock seconds per generated second of video ($\text{s}_{\text{gen}} / \text{s}_{\text{video}}$).
  - Cumulative Drift Error ($\mathcal{D}(t)$).
  - Flow Warping Consistency Error.
  - Visual Flicker Variance.

### 4.4 Baseline
- Independent dense generation of all 16 frames through full diffusion reverse process.

### 4.5 Success & Failure Criteria
- **Success Criteria:**
  - $\ge 3\times$ speedup in video generation throughput ($\text{s}_{\text{gen}} / \text{s}_{\text{video}}$ reduced by $\ge 65\%$).
  - Temporal consistency metric improved or within 3% of baseline.
  - Adaptive anchor triggering successfully prevents catastrophic drift on sudden motion changes.
- **Failure Criteria:**
  - Visible object ghosting or trailing behind moving subjects.
  - Drift accumulation causes video to turn muddy or lose structural integrity after 8 frames.

---

## 5. Experiment E: Full Foundation Video Models (Wan2.1 / LTX-Video)

### 5.1 Objective
Deploy the complete **Low-Compute Generative Runtime (LCGR)** compiler, tiered memory manager, and Generative World State on production multi-billion parameter video architectures (**Wan2.1-T2V-1.3B** and **LTX-Video-2B**) on live GPU hardware (e.g. NVIDIA A100 / RTX 4090).

### 5.2 System Implementation
- Complete LCGR 10-stage execution pipeline.
- Generative World State (GWS) tracks scene entities, camera motion, and 3D VAE caches.
- Semantic Compute Field directs 3D DiT token sparsity across 81 frames ($832 \times 480$).
- Tiered Memory Manager schedules dynamic tensor offloading between VRAM and host RAM using PCIe Gen4 bandwidth thresholds.
- Full evaluation across all 10 video prompts (`V01–V10`).

### 5.3 Variables
- **Independent Variables:**
  - Model: Wan2.1-T2V-1.3B vs. LTX-Video-2B.
  - Runtime Mode: Vanilla Baseline (Official Resident / Vanilla Offload) vs. LCGR Adaptive Plan.
  - Memory Constraint: 24 GB GPU budget vs. 12 GB GPU budget vs. 8 GB GPU budget.
- **Dependent Variables:**
  - Total Generation Latency (seconds for 5.0s video clip).
  - Seconds generated per second of output.
  - Peak VRAM allocated (GB).
  - Total PCIe transfer volume (GB).
  - Quality Metrics: Video-CLIP score, Optical Flow Consistency, Human MOS.
  - Cost Frontier Position: Quality vs. VRAM vs. Time.

### 5.4 Baseline
- Official vanilla pipeline:
  - Wan2.1: 50 flow steps, 832x480, 81 frames, full dense attention, standard offload.
  - LTX-Video: 50 steps, 768x512, 121 frames, full dense attention.

### 5.5 Success & Failure Criteria
- **Success Criteria:**
  - **Compute Target:** $\ge 40\%$ reduction in generation latency on equivalent hardware without human-perceptible quality drop ($\Delta \text{MOS} \le 0.15$).
  - **Memory Target:** Stable execution on 12 GB VRAM with $<30\%$ latency penalty relative to unconstrained 24 GB resident baseline (defeating the $4\times$ penalty of vanilla offload).
  - **Zero Crash / OOM:** 100% execution success across all 10 standardized prompts (V01–V10).
- **Failure Criteria:**
  - Planner overhead exceeds 12% of total generation time.
  - Temporal drift produces identity morphing or structural collapse in high-motion prompts (V03, V10).
  - Memory thrashing causes Out-Of-Memory (OOM) on targeted 12 GB hardware.
