# PHASE 1 THEORY SPECIFICATION: LOW-COMPUTE GENERATIVE RUNTIME (LCGR)
## Formal Mathematical Specifications, Data Structures, and Algorithmic Foundations

---

## 1. Mathematical Problem Formulation

### 1.1 Naive Formulation vs. Generalized LCGR Formulation
The naive generative optimization problem is traditionally stated as:
$$\min_{\theta, \mathbf{z}} \quad \text{ComputeCost} + \text{MemoryCost} + \text{LatencyCost} \quad \text{s.t.} \quad \mathcal{Q} \ge Q_{\text{target}}$$

This formulation is fundamentally flawed for three reasons:
1. **Dimensional Incompatibility:** Compute (FLOPs), Memory (bytes), and Latency (seconds) cannot be summed directly without rigorous economic weighting and hardware constraint boundaries.
2. **Perceptual Non-Uniformity:** Perceptual quality $\mathcal{Q}$ is treated as a global scalar, ignoring that human perception is non-uniform across spatial frequency, foveation, semantic task salience, and temporal motion.
3. **Dynamic Budget Constraints:** Hardware memory is a hard ceiling (exceeding it causes Out-Of-Memory termination, not gradual degradation), while PCIe transfer bandwidth creates non-linear latency penalties.

### 1.2 The Formal LCGR Optimization Objective
Let $\Omega = \mathcal{X} \times \mathcal{T} \subset \mathbb{R}^2 \times \mathbb{R}^+$ define the continuous spatial-temporal continuum of the generated artifact (where $\mathcal{X}$ is the spatial domain and $\mathcal{T} = [0, T]$ is the temporal interval).

We formulate generative synthesis as a **constrained multi-objective variational planning problem**:

$$\min_{\pi \in \Pi} \quad \mathcal{J}(\pi) = \int_0^T \left[ \alpha(t) \cdot \mathcal{K}(\pi, t) + \beta(t) \cdot \mathcal{B}_{\text{PCIe}}(\pi, t) \right] dt + \gamma \cdot \mathcal{T}_{\text{total}}(\pi)$$

Subject to the following strict constraints:

$$\begin{aligned}
\text{1. Perceptual Quality Bound:} \quad & \mathcal{Q}_{\text{perceptual}}(\mathbf{x}_{\text{gen}}(\pi), \mathbf{x}^*) \ge Q_{\text{target}} \\
\text{2. Spatial-Temporal Fidelity:} \quad & \mathcal{L}_{\text{perceptual}}(x, y, t) \le \epsilon_{\text{allowable}}(x, y, t), \quad \forall (x,y,t) \in \Omega \\
\text{3. Instantaneous VRAM Ceiling:} \quad & \mathcal{M}_{\text{VRAM}}(t) \le M_{\text{VRAM\_limit}}, \quad \forall t \in [0, \mathcal{T}_{\text{total}}] \\
\text{4. Host System RAM Ceiling:} \quad & \mathcal{M}_{\text{RAM}}(t) \le R_{\text{RAM\_limit}}, \quad \forall t \in [0, \mathcal{T}_{\text{total}}] \\
\text{5. Temporal Drift Bound:} \quad & \mathcal{D}_{\text{temporal}}(t) \le \delta_{\text{drift\_max}}, \quad \forall t \in [0, T]
\end{aligned}$$

Where:
- $\pi \in \Pi$ is the **Generative Computational Plan** selected by the runtime compiler from the space of admissible planning policies $\Pi$.
- $\mathcal{K}(\pi, t)$ is the instantaneous compute rate (FLOPs/s) deployed at execution time $t$.
- $\mathcal{B}_{\text{PCIe}}(\pi, t)$ is the memory bus bandwidth utilization (bytes/s) between host RAM and accelerator VRAM.
- $\mathcal{T}_{\text{total}}(\pi)$ is the total wall-clock duration to satisfy the generation goal.
- $\alpha(t), \beta(t), \gamma$ are marginal economic conversion factors matching hardware energy, memory bus contention, and user latency preferences.
- $\mathcal{L}_{\text{perceptual}}(x, y, t)$ is the spatio-temporal perceptual loss field.
- $\epsilon_{\text{allowable}}(x, y, t)$ is the allowable error envelope determined by human perceptual contrast sensitivity and semantic salience.

---

## 2. Mathematical Definition of the Semantic Compute Field (SCF)

### 2.1 The Continuous Field Formulation
The **Semantic Compute Field** $\mathcal{C}: \Omega \rightarrow [0, 1]$ is a continuous spatial-temporal scalar density field defining the normalized fraction of maximum model capacity allocated to coordinate $(x, y, t)$:

$$\mathcal{C}(x, y, t) = \sigma \left( \mathbf{w}^T \mathbf{\Phi}(x, y, t) - \theta_{\text{base}} \right)$$

Where $\sigma(z) = \frac{1}{1 + e^{-z}}$ is the sigmoid activation ensuring strict bounding in $(0, 1)$, and $\mathbf{\Phi}(x, y, t)$ is the 5-dimensional feature tuple:

$$\mathbf{\Phi}(x, y, t) = \begin{bmatrix}
\mathcal{S}_{\text{semantic}}(x, y, t) \\
\mathcal{U}_{\text{epistemic}}(x, y, t) \\
\mathcal{V}_{\text{motion}}(x, y, t) \\
\mathcal{P}_{\text{contrast}}(x, y, t) \\
\mathcal{Q}_{\text{deficit}}(x, y, t)
\end{bmatrix}$$

### 2.2 Feature Components
1. **Semantic Importance $\mathcal{S}_{\text{semantic}}(x, y, t) \in [0, 1]$:**
   $$\mathcal{S}_{\text{semantic}}(x, y, t) = \sum_{e \in \text{Entities}} \omega_e \cdot \mathbb{P}((x, y, t) \in \text{Mask}(e))$$
   Weights $\omega_e$ prioritize human visual focal points: faces ($\omega_{\text{face}} = 1.0$), hands ($\omega_{\text{hands}} = 0.95$), primary foreground subjects ($\omega_{\text{subject}} = 0.8$), textured surfaces ($\omega_{\text{texture}} = 0.4$), and homogeneous backgrounds ($\omega_{\text{sky}} = 0.1$).

2. **Epistemic Uncertainty $\mathcal{U}_{\text{epistemic}}(x, y, t) \in [0, 1]$:**
   Derived from the score matching variance across multiple stochastic perturbations or ensemble heads:
   $$\mathcal{U}_{\text{epistemic}}(x, y, t) = \frac{\mathbb{V}_{\epsilon}[\mathbf{s}_\theta(\mathbf{z}_t + \sigma_t \epsilon, t)]}{\max_{(x',y')} \mathbb{V}_{\epsilon}[\mathbf{s}_\theta(\mathbf{z}_t + \sigma_t \epsilon, t)] + \varepsilon}$$

3. **Temporal Motion Dynamic $\mathcal{V}_{\text{motion}}(x, y, t) \in [0, 1]$:**
   Normalized velocity magnitude extracted from the world state motion vectors:
   $$\mathcal{V}_{\text{motion}}(x, y, t) = \tanh \left( \frac{\|\mathbf{v}(x, y, t)\|_2}{\bar{v}_{\text{ref}}} \right)$$

4. **Human Perceptual Contrast Sensitivity $\mathcal{P}_{\text{contrast}}(x, y, t) \in [0, 1]$:**
   Calculated using Mannos-S臟rison Human Visual System (HVS) Contrast Sensitivity Function (CSF):
   $$\mathcal{P}_{\text{contrast}}(f_s) = 2.6 \cdot (0.0192 + 0.114 \cdot f_s) \cdot e^{-(0.114 \cdot f_s)^{1.1}}$$
   where $f_s$ is the local spatial frequency in cycles per degree of visual angle.

5. **Quality Deficit $\mathcal{Q}_{\text{deficit}}(x, y, t) \in [0, 1]$:**
   $$\mathcal{Q}_{\text{deficit}}(x, y, t) = \max\left(0, \frac{Q_{\text{target}}(x, y, t) - \hat{\mathcal{Q}}_{\text{current}}(x, y, t)}{Q_{\text{target}}(x, y, t)}\right)$$

### 2.3 Discretization to Execution Token Masks
To interface with transformer-based diffusion architectures (DiT), the continuous field $\mathcal{C}(x, y, t)$ is projected onto discrete patch tokens $p_{i,j,k}$ of dimension $(p_x, p_y, p_t)$:

$$\Lambda_{i, j, k} = \frac{1}{p_x \cdot p_y \cdot p_t} \iiint_{\text{Patch}(i,j,k)} \mathcal{C}(x, y, t) \, dx \, dy \, dt$$

The runtime token execution mask $\mathbf{M}_{i,j,k}^{(\ell)}$ at transformer layer $\ell$ is governed by a stochastic or top-$k$ thresholding policy:

$$\mathbf{M}_{i,j,k}^{(\ell)} = \begin{cases} 
1 & \text{if } \Lambda_{i, j, k} \ge \tau^{(\ell)}_{\text{compute}} \\
0 & \text{otherwise (Token Pruned / Reused from Cache)}
\end{cases}$$

---

## 3. Error-Driven Generation & Adaptive Termination

### 3.1 Error Representation and Quality Verification
At any generative step $s \in \{1, \dots, S\}$, the intermediate latent state is $\hat{\mathbf{z}}_s$. The runtime estimates local residual error $\mathcal{E}_s(p)$ for token patch $p$ through a dual-channel estimator:

$$\mathcal{E}_s(p) = w_1 \cdot \mathcal{E}_{\text{score\_residual}}(p) + w_2 \cdot \mathcal{E}_{\text{temporal\_inconsistency}}(p)$$

Where:
$$\mathcal{E}_{\text{score\_residual}}(p) = \left\| \mathbf{v}_\theta(\hat{\mathbf{z}}_s, s)[p] - \mathbf{v}_\theta(\hat{\mathbf{z}}_s + \delta, s)[p] \right\|_2$$
$$\mathcal{E}_{\text{temporal\_inconsistency}}(p) = \left\| \hat{\mathbf{z}}_{s, t}[p] - \mathcal{W}(\hat{\mathbf{z}}_{s, t-1}, \mathbf{v}_{t-1})[p] \right\|_2$$

### 3.2 Formal Stopping Condition: "Good Enough"
Selective refinement terminates for patch $p$ at step $s$ if and only if:

$$\mathcal{E}_s(p) \le \epsilon_{\text{allowable}}(p) \quad \lor \quad \text{MVC}_s(p) < \kappa_{\text{min}}$$

Where **Marginal Value of Computation (MVC)** is defined as:

$$\text{MVC}_s(p) = \frac{\mathbb{E}\left[ \mathcal{Q}_{s+1}(p) - \mathcal{Q}_s(p) \right]}{\Delta \text{FLOPs}(p, s \rightarrow s+1)}$$

If $\text{MVC}_s(p) < \kappa_{\text{min}}$, executing another denoising pass on patch $p$ is mathematically provable to yield sub-perceptual return per FLOP spent. The token $p$ is frozen and passed directly to the latent accumulator.

---

## 4. Temporal Delta Generation (TDG) & Drift Control

### 4.1 Delta Synthesis Formulation
Instead of computing full frame latents $\mathbf{z}_{t+1} \in \mathbb{R}^{C \times H \times W}$ independently, the runtime executes:

$$\mathbf{z}_{t+1} = \mathcal{W}\left(\mathbf{z}_t, \mathbf{v}_{t \rightarrow t+1}\right) + \mathbf{M}_{\text{innovation}} \odot \Delta \mathbf{z}_{t+1} + \mathbf{R}_{\text{residual}}$$

Where:
- $\mathcal{W}(\mathbf{z}_t, \mathbf{v})$ is a bilinear spatio-temporal backward warping operator parameterized by optical flow field $\mathbf{v}$.
- $\mathbf{M}_{\text{innovation}} \in \{0, 1\}^{H \times W}$ is a binary occlusion/disocclusion mask identifying freshly revealed scene elements.
- $\Delta \mathbf{z}_{t+1}$ is the generative innovation synthesized strictly inside the disoccluded regions.
- $\mathbf{R}_{\text{residual}}$ is the sparse high-frequency residual correcting warping distortion.

### 4.2 Accumulated Temporal Drift Control
Let the cumulative temporal drift error at frame $t$ relative to keyframe $t_0$ be:

$$\mathcal{D}(t) = \sum_{\tau = t_0}^{t-1} \left\| \mathbf{z}_{\tau+1} - \mathcal{W}(\mathbf{z}_\tau, \mathbf{v}_\tau) \right\|_1$$

**Keyframe Invalidation Condition:**
The runtime forces an anchor frame replenishment (full latent regeneration) whenever:

$$\mathcal{D}(t) > \tau_{\text{drift\_threshold}} \quad \lor \quad \frac{\sum \mathbf{M}_{\text{innovation}}}{H \times W} > 0.45$$

---

## 5. Generative World State (GWS) Schema

The Generative World State is defined formally as an immutable directed state graph:

$$\mathcal{S}_{\text{world}} = \langle \mathcal{E}, \mathcal{G}, \mathcal{A}, \mathcal{C}, \mathcal{L}, \mathcal{M}, \mathcal{T}, \mathcal{Q}, \mathcal{U} \rangle$$

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GenerativeWorldState",
  "type": "object",
  "required": ["state_id", "timestamp", "entities", "camera", "lighting", "motion_graph", "cache_registry"],
  "properties": {
    "state_id": { "type": "string" },
    "timestamp": { "type": "number" },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entity_id", "semantic_label", "bounding_polytope", "identity_embedding", "appearance_ref", "motion_ref"],
        "properties": {
          "entity_id": { "type": "string" },
          "semantic_label": { "type": "string" },
          "bounding_polytope": { "type": "array", "items": { "type": "number" } },
          "identity_embedding": { "type": "string", "description": "Normalized CLIP/Face embedding digest" },
          "appearance_ref": { "type": "string", "description": "URI to cached canonical texture/latent" },
          "motion_ref": { "type": "string", "description": "Spline or velocity trajectory" },
          "is_static": { "type": "boolean" },
          "priority_weight": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
        }
      }
    },
    "camera": {
      "type": "object",
      "required": ["extrinsic_matrix", "intrinsic_matrix", "fov", "velocity"],
      "properties": {
        "extrinsic_matrix": { "type": "array", "items": { "type": "number" } },
        "intrinsic_matrix": { "type": "array", "items": { "type": "number" } },
        "fov": { "type": "number" },
        "velocity": { "type": "array", "items": { "type": "number" } }
      }
    },
    "lighting": {
      "type": "object",
      "required": ["dominant_vector", "ambient_intensity", "color_temperature", "shadow_softness"],
      "properties": {
        "dominant_vector": { "type": "array", "items": { "type": "number" } },
        "ambient_intensity": { "type": "number" },
        "color_temperature": { "type": "number" },
        "shadow_softness": { "type": "number" }
      }
    },
    "motion_graph": {
      "type": "object",
      "required": ["flow_field_ref", "occlusion_mask_ref"],
      "properties": {
        "flow_field_ref": { "type": "string" },
        "occlusion_mask_ref": { "type": "string" }
      }
    },
    "cache_registry": {
      "type": "object",
      "properties": {
        "tier1_vram_handles": { "type": "array", "items": { "type": "string" } },
        "tier2_ram_handles": { "type": "array", "items": { "type": "string" } },
        "tier3_nvme_handles": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

## 6. Tiered Memory Cost-Benefit Model

Let data block $b$ have size $S(b)$ bytes. The decision to cache block $b$ in Tier 1 (VRAM), Tier 2 (System RAM), or Tier 3 (NVMe) is governed by:

$$\text{Tier}(b) = \arg\max_{k \in \{1, 2, 3\}} \quad \text{Utility}_k(b) - \text{LatencyCost}_k(b)$$

Where:
- $\text{Utility}_k(b) = P_{\text{hit}}(b) \cdot \mathcal{T}_{\text{recompute}}(b)$
- $\text{LatencyCost}_k(b) = \frac{S(b)}{\text{Bandwidth}(k \leftrightarrow \text{Compute})} + \mathcal{T}_{\text{sync\_lock}}$

Empirical Bandwidth Constants:
- Tier 1 (SRAM/HBM on GPU): $1,000\text{--}3,000 \text{ GB/s}$
- Tier 1 $\leftrightarrow$ Tier 2 (PCIe Gen4 x16): $31.5 \text{ GB/s}$
- Tier 2 $\leftrightarrow$ Tier 3 (NVMe PCIe Gen4): $7.0 \text{ GB/s}$

**Rule:** If $\mathcal{T}_{\text{recompute}}(b) < \frac{S(b)}{31.5 \times 10^9} + 1.2 \times 10^{-4}$ seconds, block $b$ MUST NEVER be offloaded to host RAM; it must be discarded and recomputed on-demand.
