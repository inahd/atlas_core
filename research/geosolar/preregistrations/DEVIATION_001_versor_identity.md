# DEVIATION_001 — versor-identity discovery and its consequences for PREREG_001 / PREREG_002

**Date:** 2026-05-08
**Status:** Recorded under the deviation clauses of PREREG_001 (§6) and PREREG_002 (§6).
**Lock-marker:** the first commit on this file path. Verify with `git log --follow research/geosolar/preregistrations/DEVIATION_001_versor_identity.md`.

## 1. Summary

A versor-aware (complex phasor) reformulation of the wave-field engine in `npu_engine/jyotisha_engine.py` exposed a closed-form mathematical identity that materially changes the interpretation of PREREG_001's locked reduction and the executability of PREREG_002's locked sub-family S.

This document records the discovery, the derivation, the consequences for the two pre-registrations, and a proposed (but not locked) PREREG_002b to replace the now-untestable sub-family S.

The committed numerical result of PREREG_001 (M4: r = +0.1945, n = 18,702, Holm-p = 3.4 × 10⁻¹⁵⁸, CI [+0.180, +0.209]) stands unchanged as historical artifact: those numbers were computed with the engine as it existed at PREREG_001 lock time and reflect that engine's behavior exactly. What changes is the *interpretation* of what the reduction was computing.

## 2. The closed-form identity

The pre-registered reduction is

    sun_moon_amplitude(t) = mean over k ∈ {1,2,3,4,6,7,12} of |A_k(t)|

where

    A_k(t) = compute_pair_interference(sun_long(t), moon_long(t), lagna_long(t), k)

The pre-registration specifies the function semantically as

    A_k(t) = cos(k·(lagna − sun)) + cos(k·(lagna − moon))

i.e., the real-cosine-sum form that the engine implementation returned at lock time.

The versor-aware reformulation returns a complex phasor:

    Z_k(target=θ, sources α, β) = e^(jk(θ − α)) + e^(jk(θ − β))

with `Re(Z_k) = cos(k(θ−α)) + cos(k(θ−β))` exactly equal to the previous return value, and `Im(Z_k) = sin(k(θ−α)) + sin(k(θ−β))` previously discarded.

The identity:

    |Z_k(θ, α, β)| = | e^(jk(θ−α)) + e^(jk(θ−β)) |
                  = | e^(jkθ) | · | e^(−jkα) + e^(−jkβ) |
                  = 1 · | e^(−jkα) + e^(−jkβ) |
                  = 2 |cos(k(β − α) / 2)|

The factor `e^(jkθ)` is a unit-modulus rotation; it cancels under the absolute value. The interference magnitude `|Z_k|` therefore depends **only on the source-pair angular separation `(β − α)`**, not on the target longitude `θ`.

Empirical confirmation across the 2025 10-min panchanga grid (52,560 timestamps × 10 targets × 7 k-values): the maximum spread of `sum_pairs |Z_k|` across targets at any (t, k) is **2.77 × 10⁻¹³** — machine precision. This is a closed-form identity, not a numerical coincidence.

## 3. What the locked PREREG_001 reduction actually computed

Under the engine as it existed at PREREG_001 lock time, `A_k = cos(k(lagna−sun)) + cos(k(lagna−moon))` was target-dependent: rotating the target by some angle ψ changed `A_k` because `cos(kθ)` is not a unit-modulus quantity.

Under the corrected engine, `|A_k|` becomes target-independent by the identity above. So:

- The OLD pipeline computed `|cos(k(lagna−sun)) + cos(k(lagna−moon))|` — a target-dependent scalar that happens to track Sun-Moon angular separation in a noisy, lagna-modulated way.
- The NEW pipeline (if the same scripts were re-run) would compute `2|cos(k(moon−sun)/2)|` — a target-independent scalar that depends only on the Sun-Moon angular separation and `k`.

The two scalars differ at every timestamp; they are not the same function. The OLD reduction was *not* a clean implementation of "interference magnitude at the lagna" because `|cos+cos|` is not the magnitude of an interference field — `|Z_k|` is. The OLD reduction tracked `|Re(Z_k)|`, which is the **magnetic-mode component magnitude**, not the field magnitude.

## 4. Implication for PREREG_001's M4 result

PREREG_001 reported M4 (daily SF tide range vs daily-mean Sun-Moon amplitude at the Gainesville lagna) at r = +0.1945, surviving the locked criterion. The §8 discussion flagged a caveat that k=2 embeds the M2/S2 standard tidal constituents and that "lagna-coupling vs generic Sun-Moon geometry" was an open question for PREREG_002 to discriminate.

The closed-form identity collapses that question:

- Under the corrected engine, the lagna at Gainesville contributes nothing to `|Z_k|`. The reduction is mathematically a function of (Sun-Moon separation, k) only.
- Under the original engine, the lagna *did* enter `|cos+cos|`, but only through the target-dependent floating-point pattern of the cosine sum — i.e., the lagna-coupling was a pattern of the chosen reduction's mathematical form, not a physical coupling.

The published M4 finding is therefore best read as: *"a target-rotated cosine-sum scalar tracking Sun-Moon angular separation correlates with SF daily tide range at r ≈ 0.19 over 1973–2024."* The lagna at Gainesville did not differentiate the result. The correlation is consistent with the standard semi-diurnal tidal envelope (M2 + S2), as the §8 caveat already noted, with the new identity making the caveat structural rather than open.

The committed numerical result is unaffected. The locked design behaved exactly as specified in `build_sun_moon_field*.py`. What is different is the meaning of what those numbers measured.

## 5. Implication for PREREG_002

PREREG_002 (locked at commit reachable via `git log --follow research/geosolar/preregistrations/PREREG_002_k_decomp_multi_station.md`) defined two sub-families:

### 5a. Sub-family K — k-decomposition

Locked design: per-k Pearson r between `|Z_k|` at the Gainesville lagna and SF daily tide range, for k ∈ {1, 2, 3, 4, 6, 7, 12}.

Under the new engine: the per-k reduction at Gainesville lagna becomes `2|cos(k(moon−sun)/2)|`, a Sun-Moon-only scalar. This *is still meaningful* — it discriminates whether the per-k correlation is concentrated in k=2 (M2/S2 dominance, classical tidal physics) or distributed across higher k. The lagna no longer enters, but the locked design's per-k discriminator does what the prereg said it would: separate classical vs distributed contributions.

**Sub-family K remains executable and meaningful under the new engine.** No deviation needed for K.

Under the old engine: the per-k reduction at Gainesville lagna is `|cos(k(lagna−sun)) + cos(k(lagna−moon))|`, which has the same Sun-Moon-driven core but with a floating-point lagna pattern overlaid. Running K with the old engine would test classical-vs-distributed structure with that overlay; running K with the new engine tests it without. The choice between them is a judgment call about which engine version is the canonical one.

**Recommendation:** run sub-family K under the new engine. It tests the same physics question (k=2 dominance vs distribution) more cleanly.

### 5b. Sub-family S — multi-station latitude-coupling

Locked design: per-station Pearson r between `|Z_k|` at the *station-local* lagna and the station-local daily tide range, for 6 stations (Vishakhapatnam, Chennai, Kochi, Mumbai, San Francisco, Honolulu). Discriminates lagna-coupling from generic Sun-Moon geometry.

Under the new engine: `|Z_k|` at any station's lagna reduces to `2|cos(k(moon−sun)/2)|` regardless of station coordinates. The closed-form identity makes all six stations produce **bit-for-bit identical predictor series** — no data needed to know the answer in advance. The Pearson r at each station would depend only on that station's tide-range series; differences between stations would be entirely tide-side, not lagna-side. The sub-family cannot discriminate lagna-coupling because the predictor has no station dependence.

Under the old engine: `|cos(k(station_lagna−sun)) + cos(k(station_lagna−moon))|` *does* depend on station_lagna, so per-station predictor series would differ. But the closed-form identity reveals that this dependence is structurally a floating-point pattern of the chosen reduction's mathematical form, not a physical coupling — running it under the old engine would discriminate stations only via that pattern, not via real lagna-coupling.

**Sub-family S cannot be meaningfully executed under either engine.** Under the new engine it is a closed-form no-op. Under the old engine it tests the floating-point pattern of `|cos+cos|` against itself, which is not what the pre-registration intended.

The locked PREREG_002 sub-family S is therefore retired by this deviation. Its execution is not pursued; the question it intended to answer (location-specificity of the M4 effect) requires a different reduction, proposed below as PREREG_002b.

## 6. Proposed PREREG_002b (NOT locked; for a future session)

The closed-form identity localizes target-dependent information into `Re(Z_k)` and `Im(Z_k)` separately:

- `Re(Z_k)`: broadside-radial / magnetic-mode component, target-dependent.
- `Im(Z_k)`: axial-longitudinal / dielectric-mode component, target-dependent.

Either can serve as a per-station predictor that genuinely varies with station coordinates. PREREG_002b proposes:

**Sub-family K' — per-k decomposition (replaces sub-family K, optional refinement):**
For each k ∈ {1, 2, 3, 4, 6, 7, 12}, three predictors at the Gainesville lagna against SF daily tide range:
- `|Z_k|` (closed-form: `2|cos(k(moon-sun)/2)|`, lagna-independent — tests classical tidal harmonics)
- `|Re(Z_k)|` (target-dependent magnetic-mode component)
- `|Im(Z_k)|` (target-dependent dielectric-mode component)

This expands K from 7 tests to 21 tests and discriminates whether *any* component carries lagna-specific signal once Sun-Moon geometry is held constant via the magnitude row.

**Sub-family S' — multi-station with mode-decomposed predictors (replaces sub-family S):**
For each of the same 6 stations, two predictors at the station-local lagna against station-local daily tide range:
- `|Re(Z_k)|` averaged across k ∈ {1,2,3,4,6,7,12} — magnetic-mode amplitude
- `|Im(Z_k)|` averaged across k ∈ {1,2,3,4,6,7,12} — dielectric-mode amplitude

Both are station-dependent (target enters through the rotation `e^(jkθ)` which separates Re from Im). 12 tests total.

**Combined family for Holm correction in PREREG_002b:** K' (21) + S' (12) = 33 tests at α = 0.05.

**Outcome interpretation rules** would mirror PREREG_002's §3 with the addition that mode-component splits provide a third axis (`|Z_k|` vs `|Re|` vs `|Im|`) for diagnosing where any signal lives.

The cluster-difference / outcome-D follow-up requirement (PREREG_002 §3d) carries forward into PREREG_002b unchanged.

PREREG_002b is **not locked by this deviation document.** Locking PREREG_002b is a separate session, performed before any data is touched under the proposed design.

## 7. Effect on the committed pre-registration record

- **PREREG_001 (locked at b3bad8e):** the locked design is intact and the committed M4 numerical result is intact. This deviation document records that the *interpretation* of that result (lagna-coupling vs global Sun-Moon geometry) collapses under the corrected engine: the reduction is now known to be lagna-independent in closed form. Per PREREG_001 §6, this is a deviation in interpretation, not in executed design. The locked confirmatory claim ("M4 survived; M1, M2, M3 rejected at multi-decade scale") stands as recorded.
- **PREREG_002 (locked at 05290f7):** sub-family K is reframed but still executable; sub-family S is retired by mathematical impossibility. Per PREREG_002 §6, the deviation is recorded here.
- **Engine commit:** the versor-aware engine change is committed alongside this deviation document so that the timeline is auditable: the engine change and the deviation it forced are recorded in the same commit.

## 8. Signature

Date: 2026-05-08
Author: inahd (Gainesville, FL)
Engine commit incorporating the versor decomposition is the same commit that introduces this document. PREREG_002b lock is deferred to a separate session.
