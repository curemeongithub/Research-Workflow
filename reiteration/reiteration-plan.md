---
phase: 9
document: reiteration-plan
timestamp: 2026-04-06T00:00:00Z
starting_phase: 1
---

# Reiteration Plan

## Recommended Action

**Targeted Phase 1 reiteration starting at Phase 1, re-running through Phase 8.**
The Phase 1 acquisition failure (17/30 arXiv sources wrong) is the root cause of three downstream weaknesses: thin NTK sourcing, absent adjacent generalization-bounds literature, and the E1 three-layer proof strategy error (the correct formulation is in [Ergen&Pilanci2021global], which was a user PDF and was read — but the proof strategy didn't absorb its three-layer construction). However, because the core Pilanci/Ergen corpus was fully read via user PDFs, a *targeted* (not full) Phase 1 re-run is sufficient: acquire only the 5–6 specific missing adjacent papers, re-run Phase 2 for those papers only, then re-run Phases 3–8.

---

## If Reiteration Proceeds — Starting Phase: 1 (Targeted)

### What to fix in Phase 1

**Do not re-acquire papers that are already correct.** The following sources are good and must not be touched:
- All 6 user-provided PDFs (`user-2002.10553v2`, `user-2110.05518v2`, `user-2402.03625v3`, `user-ergen21b`, `user-8652_CRONOS_Enhancing_Deep_Lea`, `user-2110.06482v3`)
- All 3 web sources (NTK blog post `lilianweng-ntk`, plus any other blogs already at `readable: true`)

**Acquire these 5 specific papers that are currently absent or mismatched:**

| Priority | Paper | arXiv ID | Why needed |
|----------|-------|----------|------------|
| P1 | Jacot, Gabriel & Hongler (2018) — "Neural Tangent Kernel: Convergence and Generalization in Neural Networks" | arXiv:1806.07572 | Primary NTK theory paper; needed to back H7/E7 NTK claims with primary source, not blog |
| P2 | Gunasekar, Lee, Woodworth & Srebro (2017) — "Implicit Regularization in Matrix Factorization" | arXiv:1705.09280 or 1710.10174 | Compression/generalization bounds directly applicable to H4; cited in Phase 5 Missing Gap A |
| P3 | Du, Zhai, Poczos & Singh (2019) — "Gradient Descent Provably Optimizes Overparameterized Neural Networks" | arXiv:1810.02054 | NTK-regime convergence; needed to precisely characterize the lazy-training prediction vs. convex duality prediction in H7 |
| P4 | Bach (2017) — "Breaking the Curse of Dimensionality with Convex Neural Networks" | arXiv:1405.4604 | The adjacent infinite-width convex NN work referenced in the literature map's research timeline; currently 404 from the blog fetch |
| P5 | Arora, Ge, Neyshabur & Zhang (2018) — "Stronger generalization bounds for deep nets via a compression approach" | arXiv:1802.05296 | The compression-based generalization framework for H4; currently cited but not sourced |

**Fetch strategy for each:**
- Use `curl -sL "https://arxiv.org/pdf/{PAPER_ID}.pdf" -o sources/{PAPER_ID}/raw.pdf` and extract via Mistral OCR.
- Do NOT use `arxiv.org/src/` tarballs (this was the failure mode in the original Phase 1 — tarballs returned wrong papers). Use direct PDF download instead.
- Verify content by grepping for the paper's title or author name in the extracted markdown before marking as `readable: true`.

**Verification step after acquisition:**
```bash
grep -i "Neural Tangent Kernel" sources/arxiv-1806.07572/content.md | head -3
grep -i "Implicit Regularization" sources/arxiv-1705.09280/content.md | head -3
grep -i "compression" sources/arxiv-1802.05296/content.md | head -3
```
If any grep returns empty, the wrong paper was acquired. Re-fetch before proceeding.

**Update manifest.yaml** to add the 5 new sources with `content_quality: ok`, then increment `readable_count` and `total_sources`.

**Critical improvement targets for Phase 1:**
1. Use direct PDF downloads, not arXiv tarballs, for all new acquisitions
2. Verify paper identity (title match) before marking readable
3. Do not re-run acquisition for the 22 already-correct sources

---

### What to fix in Phase 2

Re-run extraction only for the 5 newly acquired papers. Use Mistral OCR for PDFs. No changes needed for the 22 already-extracted sources.

---

### What to fix in Phase 3

Re-run the literature map with all 27 sources (22 existing + 5 new). The re-run agent should:

1. **Add a Section on Adjacent Theoretical Foundations** covering: Jacot et al. 2018 (NTK), Du et al. 2019 (NTK convergence), Gunasekar et al. 2017 (implicit regularization in matrix factorization), Bach 2017 (infinite-width convex NNs). This section contextualizes the Pilanci/Ergen framework against prior convex NN attempts and the NTK literature with primary sources.

2. **Revise Section 6 (Contested Areas — NTK vs. Convex Duality)** to include technical claims from Jacot et al. 2018 (the actual NTK lazy-training theorem, not blog-level description). Specifically: NTK's kernel matrix formula $\Theta = \mathbb{E}[\nabla_\theta f \nabla_\theta f^T]$ and its deterministic convergence in the infinite-width limit are the precise claims to quote.

3. **Add an entry for Gunasekar et al. 2017** to the methodology landscape section, noting its compression-based generalization bounds as the mathematical toolkit for H4. Note the explicit connection: the dual-sparsity $k^* \leq n+1$ from Carathéodory is the "description length" in Arora et al. 2018's compressed model framework.

The rest of the Phase 3 literature map can be preserved as-is; only Sections 6 and 9 need targeted updates.

---

### What to fix in Phase 7 (E1 proof strategy)

The E1 proof strategy Step 1 must be corrected. The fix does not require re-running Phase 4, 5, or 6 (the hypothesis H1 is still correct; only the proof strategy's first step is wrong). Phase 7 should be re-run with the following correction to E1:

**Current (incorrect) Step 1:**
> "Rescaling reduction: Express the rank-1 primal as $\min_\mathbf{w}\frac{1}{2}\|\sigma(X\mathbf{w})-\mathbf{y}\|^2 + \frac{\beta}{2}\|\mathbf{w}\|^2$"

**Corrected Step 1:**
> "Architecture formulation: For a standard three-layer ReLU network, the primal is $\min_{W_1, W_2, \alpha}\frac{1}{2}\|\sum_j \sigma(W_2\sigma(W_1 X))_j \alpha_j - \mathbf{y}\|^2 + \frac{\beta}{2}(\|W_1\|_F^2 + \|W_2\|_F^2 + \|\alpha\|^2)$, yielding feature maps of the form $D_{2,l}D_{1,i}X$ (products of two diagonal activation matrices, as in Ergen&Pilanci2021global Eq. 4). The hyperplane arrangement pairs $(D_{1,i}, D_{2,l})$ are the counterparts of the two-layer $D_i$ patterns; for rank-1 data, the count of distinct pairs is at most $O(n^2)$ rather than $O(n)$."

This correction propagates to the variable table in E1 (the arrangement enumeration strategy changes) and the success criteria (the biconditional is now over arrangement *pairs*, not individual arrangements). The hypothesis H1 statement itself (in Phase 6 and the final document) is correct and does not need revision — only the proof strategy step 1 and the downstream E1 DOE structure.

---

### Downstream phases to re-run

| Phase | Reason |
|-------|--------|
| Phase 2 (targeted) | Extract content from 5 newly acquired papers |
| Phase 3 | Revise literature map to incorporate Jacot et al. 2018, Du et al. 2019, Gunasekar et al. 2017, Bach 2017, Arora et al. 2018 |
| Phase 4 | Re-run gap analysis with expanded literature map (the NTK adjacent papers may strengthen Gap 2.3 evidential backing; the generalization bounds papers may elevate Gap A to a proper Tier 1 or strong Tier 2 gap) |
| Phase 5 | Re-run sanity check with expanded gap analysis (short re-run; likely few changes) |
| Phase 6 | Re-run hypotheses — H4 (generalization bounds) and H7 (NTK probe) will benefit from stronger primary-source rationale |
| Phase 7 | Re-run methodology — fix E1 Step 1 as specified above; update H7/E7 with more precise NTK characterization |
| Phase 8 | Re-run final document assembly to incorporate revised literature map sections and corrected E1 proof strategy |

---

### What to preserve

| Phase | Reason to preserve |
|-------|-------------------|
| Phase 1 — existing 22 sources | All 6 user PDFs and 3 web sources are correct and fully extracted; do not re-acquire |
| Phase 2 — existing 22 extractions | Content is correct; only augment with 5 new papers |
| Gap 1.1, 1.2, 1.3 analysis | All three Tier 1 gaps are confirmed by direct source lookups against user PDFs; adjacent work cannot change their validity |
| H1, H2, H3 hypothesis statements | Core hypotheses are well-formed; only rationale sections may require minor citation additions |
| H3, H4, H5, H6 methodologies (E3–E6) | These experiments are not affected by the NTK or generalization bounds sourcing gap |

---

## Approval Prompt

> **To proceed with reiteration:** instruct the pipeline with "Approve reiteration plan and begin re-run."
>
> **To modify before proceeding:** specify which papers to acquire or which proof-strategy correction to adjust.
>
> **To skip reiteration (accept current results):** instruct "Accept current pipeline output, no reiteration needed."

Note: If you accept the current output, the E1 three-layer proof strategy error (Step 1) should at minimum be patched in the final document before submission to any research audience, even without a full Phase 1 re-run. This is a single-paragraph fix that can be applied directly to `synthesis/final-document.md` and `synthesis/methodology.md`.
