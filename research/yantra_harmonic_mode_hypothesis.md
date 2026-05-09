# Yantra Harmonic-Mode Hypothesis: Test Report

**RESEARCH-018** | 2026-05-01 | Computed
**Hypothesis tested**: The 15 Nityā yantras are harmonic-mode views of one underlying Sri Yantra substrate, rather than 15 separate yantras.

---

## 0. Background Premise — Source Audit

The framing prompt cites two background claims:

1. *"yantra_eigenvalue_exploration.md established Sri Yantra emerges at lunisolar gear k=12.368, 85% alignment at Ekadashi"*
2. *"Two-source-interference-v3.md established wave matrix rank=15=Nitya count"*

**Audit:**

- Claim 1 is **NOT in the cited file**. `yantra_eigenvalue_exploration.md` covers: graha yantras as `Lo_Shu + k·J`, the magic constant `M = 15 + 3k`, the `±2√6` spectral invariant, Kronecker scaling `M_n = M_1^n`, the Brahmasthāna theorem (uniform eigenvector at every level), the navagraha 9×9 composite (rank 5, eigenvalues `{81, ±14.697, 0×4}`), and graha-coherence ratios (Sun=0.327 most polarized, Ketu=0.126 most coherent). **It does not contain the strings "12.368", "85%", or "Ekadashi"**, nor any Sri-Yantra-alignment metric. Verified by `grep -n "12.368\|85%\|Ekadashi" research/yantra_eigenvalue_exploration.{md,json}` returning empty.
- Claim 2 is partially supported. `two-source-interference-v3.md` Finding 10 reports `S₁ = 141.0, S₂ = 10.6 (ratio 13.3:1)` for the 27×30 wave matrix's top two singular values, with the rank-1 envelope being a Sun-Moon phase signal. Finding 12 separately notes the wave-system "effective rank 15" in the orthogonality discussion with Panchaka. So the rank-15 claim has support but isn't the dominant SVD result; rank-1 dominates by ~13×.

**Status:** Claim 1 is **SOURCE_NEEDED** — the cited prior result does not exist in the file. The hypothesis tests below were run **without** that prior baseline, and any Sri Yantra reference is constructed from scratch with explicit caveats.

---

## 1. Methodology

**Code re-used:**
- `npu_engine/geometry/cut_and_project.py` — `project_nfold(N, phase, k, size)` for per-tithi multigrid fields and `project_sri_yantra` for the full superposition.
- `npu_engine/jyotisha_engine.py` `compute_pair_interference` was reviewed but the per-graha pair interference is orthogonal to the 2D N-fold projection used here; it was not called.
- `datasets/cosmology/nitya_yantra_geometry.csv` for traditional petal counts.

**New computational infrastructure:**
- `research/scripts/yantra_harmonic_mode_tests.py` — angular FFT (polar resample with order-3 spline interpolation via `scipy.ndimage.map_coordinates`, then 1D FFT averaged across 40 concentric rings from `r=0.30·R` to `r=0.90·R`). Without spline interpolation, pixel-grid aliasing produced spurious uniform peaks at `k=24, 32, 36` across all tithis (initial run; corrected).
- Synthetic 9-triangle Sri Yantra reference (4 upward + 5 downward equilateral triangles inscribed in a circle). The exact triangle scales of "the" Sri Yantra are mathematically over-constrained — different traditions use different proportions and producing the canonical 24 intersection points exactly is famously a near-impossible geometric problem. **The synthetic reference is a constructive approximation, not a canonical geometry.**

**Parameters:** field size 512×512, spatial frequency `k = 5.0` (~3 oscillations across the disk — chosen so N-fold harmonics are genuinely visible in the FFT; lower `k` gives a too-smooth field where ring-FFTs have insufficient signal).

**Numerical artifacts in `research/yantra_harmonic_mode_results.json`** for full per-tithi data.

---

## 2. TEST 1 — Petal-count prediction

**Method.** For each tithi `t ∈ {1..15}`, generate `project_nfold(N=DEVI_N[t], phase=2π(t-1)/15)`. Compute angular power spectrum. Extract top-3 and top-8 dominant modes. Compare to `petal_count` from `nitya_yantra_geometry.csv`.

**Results table:**

| Tithi | DEVI_N | Trad. petals | Top-3 FFT modes | Petal in top-3? |
|-------|--------|--------------|-----------------|-----------------|
| 1  | 3  | 8  | [6, 12, 5]  | ✗ |
| 2  | 6  | 16 | [6, 12, 5]  | ✗ |
| 3  | 3  | 8  | [6, 12, 5]  | ✗ |
| 4  | 3  | 8  | [6, 12, 5]  | ✗ |
| 5  | 8  | 12 | [8, 1, 7]   | ✗ |
| 6  | 6  | 8  | [6, 12, 5]  | ✗ |
| 7  | 7  | 8  | [1, 14, 2]  | ✗ |
| 8  | 8  | 8  | [8, 1, 7]   | ✓ |
| 9  | 9  | 8  | [1, 2, 18]  | ✗ |
| 10 | 10 | 12 | [10, 1, 9]  | ✗ |
| 11 | 11 | 8  | [1, 2, 3]   | ✗ |
| 12 | 12 | 8  | [12, 1, 11] | ✗ |
| 13 | 13 | 8  | [1, 2, 3]   | ✗ |
| 14 | 14 | 32 | [1, 14, 2]  | ✗ |
| 15 | 15 | 16 | [1, 2, 3]   | ✗ |

**Aggregate match rates:**
- Traditional petal in top-3 FFT modes: **1/15** (only T8, where DEVI_N=8 = petals=8 trivially)
- Traditional petal in top-8 FFT modes: **4/15**
- DEVI_N or its integer harmonic in top-3: **12/15** (the FFT correctly resolves the multigrid's N-fold structure)

**Verdict — REFUTED.** The harmonic decomposition correctly identifies the field's N-fold mode (DEVI_N or 2N harmonic) for 12/15 tithis, but **traditional petal counts are not the FFT-dominant modes**. Petal counts cluster heavily at 8 (10 of 15 tithis have petals=8) regardless of DEVI_N, while FFT modes track DEVI_N. The petal count is set by iconographic tradition (Dakshinamurti Samhita pattern: triangle + 8 petals + bhupura is the dominant template), not by the harmonic content of an underlying substrate.

**Attestation:** OBSERVED (the FFT mode rates and petal-count comparisons are direct measurements). The interpretation that petals are iconographic-tradition-bound is SYNTHESIS.

---

## 3. TEST 2 — Superposition reconstruction

**Method.** Compute composite = Σ over `t ∈ {1..15}` of `project_nfold(DEVI_N[t], phase=2π(t-1)/15)`. Compare to:
1. `project_sri_yantra(k=5.0)` — the in-code superposition (NB: same construction class; this is an implementation-consistency check, not independent validation).
2. Synthetic 9-triangle Sri Yantra reference (constructive).

**Results:**

| Metric | Value |
|--------|-------|
| Pearson(composite, project_sri_yantra) | **1.000** (tautological — same construction) |
| Pearson(composite, synthetic 9-triangle) | **−0.091** |
| Composite local maxima | 14 |
| Synthetic 9-triangle local maxima | 58,457 (binary-plateau artifact of mask-based reference; not a meaningful count) |
| Sri Yantra canonical region count | 44 (43 sub-triangles + bindu) |
| Composite top-5 angular modes | (6, 13.13), (8, 1.66), (1, 1.47), (10, 0.77), (12, 0.33) |

**Verdict — NOT SUPPORTED.** The composite of 15 N-fold fields has near-zero correlation with the synthetic 9-triangle Sri Yantra geometry (`r = −0.09`). The local maxima count of 14 is one less than the Nitya count (15) and unrelated to the Sri Yantra's 44 regions. The composite is structurally a 6-fold-dominant interference pattern (top mode `k=6` with power 13.1, next mode `k=8` at power 1.7 — an 8× drop), not a 9-triangle Sri Yantra geometry.

**Caveats that limit this test:**
1. The synthetic 9-triangle reference is a constructive choice. Different triangle scales would give different correlation values. Without a canonical raster of "the Sri Yantra," any reference is approximate.
2. Pearson correlation between a smooth interference pattern and a binary triangle-mask is biased toward zero because the structures live at different statistical scales (smooth gradient vs sharp edges). A more sophisticated metric (mutual information, structural similarity index, region-count comparison after binarization) might give different numbers — though directionally the result is unlikely to flip from "moderate match" to "strong match."
3. The `project_sri_yantra` correlation of 1.0 is **not** evidence — that function literally implements the same superposition my composite does. The agreement is implementation-checkout, not hypothesis validation.

**Attestation:** OBSERVED for the numerical metrics. The interpretation that "superposition does not reconstruct the Sri Yantra geometry" is SYNTHESIS, with the caveat that the reference geometry is itself constructive.

---

## 4. TEST 3 — Substrate mode-dominance verification

**Method.** Two parts:
- **Part A**: Generate the composite substrate. Compute angular FFT. For each unique value `N ∈ DEVI_N` (i.e., `{3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}`), report whether `N` appears in the substrate's top-20 modes and at what rank/power.
- **Part B (sanity)**: For each tithi `t`, generate `project_nfold(DEVI_N[t])`. Check that its dominant FFT mode is `DEVI_N[t]` or an integer harmonic — confirms the FFT methodology is reading N-fold structure correctly.

**Part A — substrate decomposition:**

| N | Tithis with this N | In substrate top-20? | Rank | Power |
|---|-------------------|----------------------|------|-------|
| 3  | T1, T3, T4 (×3)   | ✓ (rank 16)         | 16   | 0.000 |
| 6  | T2, T6 (×2)       | ✓ (rank 1)          | 1    | 13.133 |
| 7  | T7 (×1)           | ✓                    | 7    | 0.118 |
| 8  | T5, T8 (×2)       | ✓                    | 2    | 1.659 |
| 9  | T9 (×1)           | ✓                    | 8    | 0.029 |
| 10 | T10 (×1)          | ✓                    | 4    | 0.768 |
| 11 | T11 (×1)          | ✓                    | 10   | 0.008 |
| 12 | T12 (×1)          | ✓                    | 5    | 0.331 |
| 13 | T13 (×1)          | ✓                    | 13   | 0.002 |
| 14 | T14 (×1)          | ✓                    | 11   | 0.004 |
| 15 | T15 (×1)          | ✓                    | 15   | 0.000 |

All 11 unique DEVI_N values appear as detectable peaks in the substrate's top-20 modes. **However**, the powers span ~5 orders of magnitude: N=6 dominates at power 13.1 (8× the next, N=8), while N=3 and N=15 register at numerically zero power (rounded to 3 decimals; their detection is rank-only, not magnitude-meaningful).

**Why N=3 nearly cancels** despite multiplicity 3: the three N=3 tithis are T1 (phase 0), T3 (phase `4π/15`), T4 (phase `6π/15`). The k=3 angular component picks up the factor:
```
1 + cos(3·4π/15) + cos(3·6π/15) = 1 + cos(12π/15) + cos(18π/15)
                                ≈ 1 + (−0.309) + (−0.809) = −0.118
```
Near-destructive interference. The three N=3 tithis nearly cancel each other in the substrate's k=3 mode — a non-trivial structural feature: the substrate's `phase = 2π(t-1)/15` distribution causes systematic phase cancellation of the most-multiply-occurring N value.

**Part B — per-tithi dominance sanity:**

12/15 tithis show DEVI_N or its integer harmonic as the top FFT mode. The 3 failures are T11, T13, T15 (N = 11, 13, 15) — high-N values where, at our spatial frequency `k=5` and image size 512, the N-fold modes are not well-resolved within the disk's available radial range. At higher `k` or larger image, these would likely resolve correctly.

**Verdict — PARTIALLY SUPPORTED.**

What is supported: The substrate's spectral content does include all DEVI_N values as detectable peaks (Part A all-✓). The FFT methodology is sound for low-to-mid N (Part B 12/15 pass).

What is unsupported: The hypothesis that the substrate cleanly decomposes into 15 equal-status N-fold components is contradicted by the **5-order-of-magnitude power spread**. The substrate is dominated by N=6 (which has multiplicity 2 from T2/T6 — but multiplicity alone doesn't explain the 13.1 / 1.7 ≈ 8× gap to the next mode). Multiplicity-1 high-N components (N=11, 13, 14, 15) appear at near-zero power. The substrate is more accurately described as "dominated by N=6 with weaker contributions from N=8, 10, 12, with the high-N components present but barely detectable."

**Attestation:** OBSERVED for the spectral measurements. The phase-cancellation analysis for N=3 is OBSERVED (algebra is direct). The interpretation that "high-N components are barely detectable" is OBSERVED at the chosen `k`/`size`; whether this generalizes is SYNTHESIS.

---

## 5. Honest Assessment

**The hypothesis as a unified statement** ("the 15 yantras are harmonic-mode views of one underlying Sri Yantra substrate") **is not confirmed by these tests.**

Component-wise:

| Sub-claim | Verdict | Notes |
|-----------|---------|-------|
| (a) Petal counts predicted by harmonic modes | **REFUTED** | 1/15 match rate. Petals are iconographic-tradition (mostly 8), independent of FFT modes. |
| (b) 15-fold superposition reconstructs Sri Yantra | **NOT SUPPORTED** | r = −0.09 vs synthetic 9-triangle. Composite has 14 local maxima, not 44 regions. |
| (c) Substrate empirically contains all DEVI_N components | **PARTIALLY SUPPORTED** | All 11 unique N values present, but powers span 5 orders of magnitude; substrate is N=6-dominant, not equal-mode. |
| (d) `project_nfold(N)` shows N as dominant mode (FFT sanity) | **CONFIRMED** | 12/15 tithis pass; failures are high-N (≥11) at chosen `k`/`size`. |

**What this means structurally:**

1. The 15 Nityā yantras are NOT a clean modal decomposition of a single Sri Yantra geometry. They are 15 individually-symmetric multigrid fields with different N values. Their superposition does not produce the 9-triangle Sri Yantra; it produces a different object — a 6-fold-dominant interference pattern with 14 local maxima.
2. The traditional petal counts in `nitya_yantra_geometry.csv` follow iconographic patterns (template: triangle + 8 petals + bhupura, with notable exceptions at T2, T5, T10, T14, T15 having 16/12/12/32/16 petals). These do NOT track DEVI_N or any FFT-dominant harmonic. The petal-count is a separate classical-text-derived feature, not a derived-from-substrate feature.
3. The substrate-as-superposition has a structural feature uncovered here: N=3 components phase-cancel due to the `2π·(t-1)/15` phase distribution. Three Nityas (T1 Kāmeśvarī, T3 Nityaklinnā, T4 Bheruṇḍā) all have N=3, but their combined k=3 mode is ~zero. **If** the hypothesis were that the substrate has equal weight at each N, this is the strongest single piece of negative evidence.

**What might salvage a weaker version of the hypothesis:**

- If "Sri Yantra substrate" is defined as `project_sri_yantra` itself (i.e., the in-code superposition), then by construction the 15 yantras are its 15 components. This is true tautologically and is not what these tests examine.
- If "harmonic-mode view" is defined relationally rather than reconstructively (each Nityā's yantra = one component contributing to the substrate, without requiring that the substrate look like Sri Yantra), then Test 3 Part A supports this: all 11 unique N values are detectable in the substrate. But this weaker claim doesn't deliver the "Sri Yantra emerges" payoff implied in the framing.
- A different mode of reconstruction (multiplicative composition, or weighted sum with non-uniform weights to balance the high/low N power spread) could give a stronger Sri Yantra match. This was not tested.

**What was NOT tested (for completeness):**

- Comparison against an actual canonical Sri Yantra raster (none exists in the dataset).
- Higher-order spectral methods (radial FFT, 2D FFT in polar coordinates, wavelet decomposition).
- The lunisolar-gear claim (k=12.368, the actual ratio of tropical-year/synodic-month) was not exercised — the cited prior result was not findable in the source file. If a test of "Sri Yantra emerges at k≈12.37" is desired, it would need to be set up de novo.
- Comparison to two-source interference fields from `jyotisha_engine.compute_pair_interference` — the multigrid fields used here are 2D spatial fields, while the wave-interference engine works on 1D zodiacal angle. Cross-comparison would require a spatial extension of the wave engine.

---

## 6. Recommendations

1. **Stop calling the 15 Nityā yantras "harmonic-mode views" of a single Sri Yantra.** The current evidence does not support this framing. They are 15 distinct multigrid fields whose superposition is one specific object (the 6-fold-dominant interference pattern produced by `project_sri_yantra` in code), not the canonical 9-triangle Sri Yantra geometry.
2. **Petal counts should be sourced from iconographic tradition, not derived from harmonic modes.** The two are decoupled. The current `nitya_yantra_geometry.csv` already records traditional petal counts, attested or labelled SYNTHESIS — that's the right approach.
3. **If a substrate-based formal model is desired**, the strongest available result is Test 3 Part A: the substrate spectrum contains peaks at all DEVI_N values. This is a valid weak claim. A stronger claim requires either weighting the components to balance the power spread or finding a different reconstruction operator (multiplication, convolution, tile-substitution) that does converge on Sri Yantra geometry.
4. **The k=12.368/85% Ekadashi background claim should be either sourced or retracted.** It is currently unsourceable in the cited file. If it exists in another paper or chat-history note, that source should be added to research/ before being cited as established.

---

## Attestation summary

- **OBSERVED**: All numerical FFT results, Pearson correlations, region counts, mode rankings, phase-cancellation algebra (research/yantra_harmonic_mode_results.json captures full output).
- **SYNTHESIS**: Interpretive verdicts ("REFUTED", "NOT SUPPORTED", "PARTIALLY SUPPORTED"); the analysis of why the synthetic 9-triangle reference is approximate; the recommendation that petal counts are iconographic.
- **SOURCE_NEEDED**: The cited prior finding "k=12.368, 85% alignment at Ekadashi" — not located in the cited file. The synthetic Sri Yantra reference triangle scales (constructive choice).
- **SPECULATIVE**: That a different reconstruction operator (multiplicative, weighted, substitution-based) might salvage a stronger version of the hypothesis. Untested.

---

## Files produced

- `research/scripts/yantra_harmonic_mode_tests.py` — runnable test script.
- `research/yantra_harmonic_mode_results.json` — full numerical results.
- `research/yantra_harmonic_mode_hypothesis.md` — this document.

To re-run: `python3 research/scripts/yantra_harmonic_mode_tests.py` from repo root.
