# Quality Evaluation Protocol for Generative Baselines

This document formalizes the multidimensional quality evaluation methodology for baseline image and video generation in Phase 1. In accordance with scientific discipline, this protocol is fixed upfront.

---

## 1. Image Quality Evaluation Methodology

### Metrics & Criteria
1. **Prompt Adherence (Semantic Fidelity):**
   - *Method:* Multimodal semantic similarity scoring.
   - *Automated Tool:* CLIP ViT-B/32 or ViT-L/14 cosine similarity between text prompt embedding and output image embedding:
     $$\text{CLIP-Score} = \max(0, \cos(e_{\text{text}}, e_{\text{image}})) \times 100$$
   - *Score Range:* 0.0 to 100.0 (Higher is better; baseline expectation: 28.0 - 34.0).
2. **Visual Quality & Photorealism:**
   - *Criteria:* Clean edge definition, texture detail, lighting consistency, absence of blurring.
   - *Scale:* 1 to 5 Likert scale (1 = completely corrupted, 5 = photorealistic/commercial quality).
3. **Artifact Rate:**
   - *Criteria:* Percentage of generations exhibiting visible structural flaws (aberrant halos, tiling artifacts, color quantization bands).
   - *Scale:* 0% to 100% (Lower is better).
4. **Anatomical Correctness (Human Hands & Faces - I02, I03):**
   - *Criteria:* Hand geometry error count (polydactyly, merged fingers, unnatural bone articulation).
   - *Scale:* Count of anatomical errors per generated human figure.

---

## 2. Video Quality Evaluation Methodology

### Metrics & Criteria
1. **Prompt Adherence:**
   - *Method:* Frame-averaged CLIP similarity across all sampled frames:
     $$\text{Video-CLIP} = \frac{1}{T} \sum_{t=1}^T \cos(e_{\text{text}}, e_{\text{frame}_t})$$
2. **Temporal Consistency (Motion Coherence):**
   - *Criteria:* Smoothness of spatial transitions between consecutive frames; absence of sudden structural shape-shifting.
   - *Automated Metric:* Optical Flow Warping Error (Flow Warp L1/L2) between adjacent frames $t$ and $t+1$.
   - *Scale:* 1 to 5 (1 = chaotic morphing, 5 = smooth cinematic continuity).
3. **Flicker Rate:**
   - *Criteria:* High-frequency luminance or color shifts across successive frames.
   - *Automated Metric:* Inter-frame histogram divergence.
   - *Scale:* 0.0 (zero flicker) to 1.0 (severe strobe).
4. **Identity & Object Persistence (V09, V03):**
   - *Criteria:* Maintenance of facial identity, costume colors, and background landmark geometry throughout the video duration.
   - *Scale:* 1 to 5 (1 = identity completely lost within 1s, 5 = perfect persistence across all 5s).
5. **Physical Motion Realism (V02, V10):**
   - *Criteria:* Plausibility of physical dynamics (gravity, momentum, fluid mechanics, animal locomotion).
   - *Scale:* 1 to 5.

---

## 3. Human Evaluation Protocol
- **Evaluator Pool:** 3 independent blind evaluators.
- **Protocol:** Side-by-side randomized blind presentation without model labels.
- **Aggregation:** Mean Opinion Score (MOS) across all evaluators, with Inter-Rater Reliability measured via Fleiss' Kappa ($\kappa$).
