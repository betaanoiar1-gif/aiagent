# PHASE 1 RESEARCH HYPOTHESES: LOW-COMPUTE GENERATIVE RUNTIME (LCGR)
## Formal Falsifiable Scientific Hypotheses

---

### Hypothesis H1: Saliency-Gated Spatial Token Pruning in Diffusion Transformers
- **Hypothesis ID:** `HYP-LCGR-01`
- **Statement:** Allocating computation dynamically across spatial patches based on a Semantic Compute Field reduces total inference FLOPs by at least 40% compared to uniform grid attention, with a perceptual degradation ($\Delta \text{LPIPS}$) not exceeding 0.03.
- **Mechanism:** In transformer-based diffusion models (DiT), homogeneous and low-saliency background regions (e.g. sky, calm water, out-of-focus background) achieve structural convergence within the first 15% of denoising steps. Gating self-attention token density via $\mathcal{C}(x,y,t)$ eliminates redundant quadratic $O(N^2)$ token interactions in non-focal patches while concentrating full expressive capacity on semantic focal points (faces, hands, focal subjects).
- **Expected Effect:** Total FLOPs decrease by $40\%\text{--}55\%$; peak VRAM during attention computation decreases by $30\%\text{--}45\%$; human perceptual quality score remains indistinguishable in double-blind testing.
- **Required Measurement:**
  - Floating point operations per sample (TFLOPs via hardware performance counters / PyTorch profiler).
  - Learned Perceptual Image Patch Similarity (LPIPS) relative to dense baseline.
  - Mean Opinion Score (MOS) from blind human evaluations across 20 prompts.
- **Falsification Condition:** The hypothesis is falsified if reducing FLOPs by $\ge 40\%$ causes $\Delta \text{LPIPS} > 0.05$, or if the computational overhead of computing and thresholding the Semantic Compute Field exceeds 8% of the computational savings.

---

### Hypothesis H2: Optical-Flow Compensated Temporal Delta Generation
- **Hypothesis ID:** `HYP-LCGR-02`
- **Statement:** Synthesizing video sequences via motion-compensated latent warping combined with localized innovation generation ($\Delta \mathbf{z}_t$) reduces the average compute cost per second of generated video by at least $3.5\times$ compared to full independent frame generation, while maintaining temporal consistency metrics (Flow Warp Error) within 5% of the dense baseline.
- **Mechanism:** Video sequences exhibit extreme temporal redundancy; adjacent frames differ primarily by coordinate translation rather than semantic innovation. By propagating previous latent representations through backward optical flow warping and restricting the generative denoising process to disoccluded masks ($\mathbf{M}_{\text{innovation}}$) and sparse residual details ($\mathbf{R}_{\text{residual}}$), the active number of synthesized tokens is reduced by $65\%\text{--}80\%$ on non-keyframe steps.
- **Expected Effect:** Latency per output second drops from $\approx 48\text{ s/s}$ to $\le 14\text{ s/s}$; optical flow warping error remains bounded ($\Delta \text{FlowWarpError} \le 0.05$); visual flicker decreases due to explicit state propagation.
- **Required Measurement:**
  - Wall-clock seconds generated per second of output ($\text{s}_{\text{compute}} / \text{s}_{\text{video}}$).
  - Inter-frame optical flow warping error ($L_1$ norm of warped frame difference).
  - Temporal flicker variance using high-frequency luminance Fourier analysis.
- **Falsification Condition:** The hypothesis is falsified if cumulative warping error causes noticeable structural drift or phantom motion artifacts requiring keyframe replenishment frequency higher than 1 every 4 frames, or if the runtime cost of optical flow estimation and disocclusion masking exceeds 25% of full-frame generation cost.

---

### Hypothesis H3: Marginal Value of Computation (MVC) Stopping Condition
- **Hypothesis ID:** `HYP-LCGR-03`
- **Statement:** Terminating the reverse diffusion process when the local Marginal Value of Computation ($\text{MVC}_s(p) = \frac{\Delta \mathcal{Q}}{\Delta \text{FLOPs}}$) drops below a calibrated threshold $\kappa_{\text{threshold}}$ eliminates at least 35% of total denoising steps without statistically significant drop in prompt adherence (CLIP Score drop $\le 0.5$ points).
- **Mechanism:** In continuous-time diffusion and flow matching, early steps establish global composition and high-level semantics, while late steps perform subtle high-frequency detail refinement. For many prompt classes and background regions, late-stage score updates contribute imperceptible changes that fall below the Human Visual System Contrast Sensitivity threshold ($f_s$). Stopping computation as soon as the expected perceptual return per FLOP drops below $\kappa_{\text{threshold}}$ eliminates redundant late-stage iterations.
- **Expected Effect:** Total reverse sampling steps reduced from 50 to an average of 22–32 steps; total generation latency reduced by $35\%\text{--}50\%$; CLIP text-image alignment score preserved within $98.5\%$ of 50-step baseline.
- **Required Measurement:**
  - Effective number of executed forward steps per token patch.
  - CLIP-Score (ViT-L/14) on standardized prompt dataset.
  - LPIPS and PSNR distance to 100-step over-sampled ground truth.
- **Falsification Condition:** The hypothesis is falsified if early-terminated samples exhibit visible blurriness, contrast loss, or semantic drift that causes blind evaluators to prefer the fixed 50-step baseline with $p < 0.01$ (binomial test), or if the uncertainty estimator fails to trigger early termination on $\ge 80\%$ of background tokens.

---

### Hypothesis H4: World-State Component Invalidation vs. Full Regeneration
- **Hypothesis ID:** `HYP-LCGR-04`
- **Statement:** Representing scenes as a structured Generative World State (GWS) and executing partial recomputation via a directed dependency graph achieves $\ge 4\times$ speedup when updating localized scene elements (e.g. camera angle change or clothing alteration) compared to end-to-end diffusion regeneration, with zero identity drift in untouched components.
- **Mechanism:** Standard diffusion models treat the entire image/video as an undifferentiated tensor $\mathbf{x} \in \mathbb{R}^{C \times H \times W}$. In a structured GWS, identity, background geometry, camera extrinsic matrix, and dynamic objects are separated into distinct nodes in a DAG. Modifying a parent node (e.g. camera extrinsic) invalidates only downstream projection nodes, preserving canonical identity embeddings and background texture caches.
- **Expected Effect:** Interactive editing latency drops by $75\%\text{--}85\%$; facial identity verification (ArcFace cosine similarity) between original and edited frames remains $\ge 0.95$ (near-perfect identity preservation).
- **Required Measurement:**
  - Partial recomputation latency (seconds) vs end-to-end full regeneration latency.
  - DeepFace / ArcFace identity cosine similarity on modified vs unmodified frames.
  - Pixel variance on un-invalidated regions ($\text{MSE} \approx 0$ on preserved background).
- **Falsification Condition:** The hypothesis is falsified if localized re-rendering introduces visible boundary seam artifacts along the perimeter of the invalidated mask that cannot be resolved within a single 3-step blending pass, or if identity drift occurs ($\text{ArcFace} < 0.85$).

---

### Hypothesis H5: Multi-Level Progressive Refinement Quality Escalation
- **Hypothesis ID:** `HYP-LCGR-05`
- **Statement:** A 4-level progressive generation ladder ($L_0 \rightarrow L_1 \rightarrow L_2 \rightarrow L_3$) enables the runtime to satisfy 60% of arbitrary user requests at Level 1 or Level 2, cutting median energy and compute consumption by $\ge 50\%$ relative to unconditional full-pipeline execution ($L_3$).
- **Mechanism:** User quality requirements are heterogeneous; thumbnail browsing, rapid storyboarding, and draft previews do not require $L_3$ high-frequency fine detailing. By compiling user quality intent into a formal contract ($Q_{\text{target}}$) and escalating computation sequentially through low-resolution latent drafting ($L_1$), standard diffusion ($L_2$), and selective patch refinement ($L_3$), the runtime terminates processing as soon as the contract is satisfied.
- **Expected Effect:** Median compute consumption over a representative query distribution is halved; Time-To-First-Preview (TTFP) drops from $2.5\text{ s}$ to $\le 0.15\text{ s}$ (via $L_0/L_1$).
- **Required Measurement:**
  - Distribution of compute energy (Joules / FLOPs) across a synthetic query load with varying quality thresholds.
  - Time-To-First-Preview (TTFP) in milliseconds.
  - User satisfaction rate under progressive preview versus batch waiting.
- **Falsification Condition:** The hypothesis is falsified if Level 1/Level 2 drafts are so visually unrepresentative of final Level 3 semantics that users reject the progressive preview as uninformative, or if cascading from $L_1$ to $L_3$ costs $>15\%$ more total compute than generating $L_3$ directly.

---

### Hypothesis H6: Bandwidth-Aware Dynamic Tensor Offloading Threshold
- **Hypothesis ID:** `HYP-LCGR-06`
- **Statement:** An analytical memory offloading scheduler that enforces the transfer condition $\mathcal{T}_{\text{recompute}} > \mathcal{T}_{\text{PCIe}} + \mathcal{T}_{\text{sync}}$ prevents catastrophic generation slowdowns on low-VRAM GPUs ($\le 8\text{ GB}$), restricting latency degradation to $\le 35\%$ compared to standard pipeline offloading which incurs $300\%\text{--}500\%$ slowdowns.
- **Mechanism:** Standard PyTorch/Diffusers offloading blindly flushes entire layers to system RAM between forward passes without evaluating whether recomputing the activation from low-dimensional latent seeds is faster than paying the round-trip PCIe transfer penalty. By computing the exact crossover threshold between kernel execution time and PCIe bus throughput, LCGR selectively discards easily recomputed tensors and reserves PCIe bandwidth exclusively for heavy spatial KV-caches.
- **Expected Effect:** Generation slowdown on 8 GB GPUs is constrained to $\le 1.35\times$ baseline, rather than the $4.0\times$ baseline slowdown observed in vanilla Wan2.1 offload.
- **Required Measurement:**
  - Generation time on a constrained VRAM environment (e.g. 8 GB or 12 GB GPU) with LCGR dynamic scheduler vs standard `enable_model_cpu_offload()`.
  - Total gigabytes transferred across the PCIe bus per generation.
  - Maximum VRAM allocated during run.
- **Falsification Condition:** The hypothesis is falsified if the dynamic scheduler fails to prevent Out-Of-Memory (OOM) on an 8 GB target, or if the overhead of tracking tensor lifetimes and bus contention exceeds 10% of total inference time.
