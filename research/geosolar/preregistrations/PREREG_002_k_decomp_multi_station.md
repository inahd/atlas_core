# PREREG_002 — k-decomposition and multi-station latitude-coupling tests for the Sun-Moon × tide-range survivor (M4)

**Pre-registration date:** 2026-05-08
**Lock-marker:** the first commit on this file path. Verify with `git log --follow research/geosolar/preregistrations/PREREG_002_k_decomp_multi_station.md`. Subsequent commits are deviations under §6.

## 1. Preamble

This pre-registration locks the analysis design for two confirmatory follow-up tests motivated by the M4 (tide range × Sun-Moon amplitude at Gainesville lagna) survivor in PREREG_001's multi-decade analysis (locked at b3bad8e, results at research/geosolar/multidecade_1973_2024/MULTIDECADE_M1_M4_ANALYSIS.md).

The M4 result (r = +0.1945, n = 18,702, Holm-p = 3.4 × 10⁻¹⁵⁸, CI [+0.180, +0.209], stable across solar-cycle phases) is methodologically clean but interpretively ambiguous. The Sun-Moon raw-amplitude scalar averages |A_k| across k ∈ {1, 2, 3, 4, 6, 7, 12}; the k=2 harmonic embeds the standard semi-diurnal tidal constituents (M2 lunar, S2 solar) that drive ordinary tidal physics. Some fraction of M4's r is therefore expected from established mechanics, not from a novel coupling.

Two questions remain open:
- **k-decomposition.** Is the r concentrated in k=2 (consistent with classical tidal physics), or distributed across multiple k (suggesting Atlas's wave-field reduction captures something beyond standard harmonic tidal theory)?
- **Multi-station latitude coupling.** Does the lagna-locked Sun-Moon amplitude predict tide range *at the local station's lagna* across multiple geographically distinct stations? If yes, the lagna-coupling claim is supported. If the correlation is uniform across stations regardless of lagna, then "lagna at Gainesville" was doing no work and the effect is generic Sun-Moon geometry.

This pre-registration locks the design before any of the new data (additional stations) is fetched and before per-k decomposition is computed.

## 2. Pre-specified test design (locked)

### 2a. Sub-family K — k-decomposition (7 tests)

For each k ∈ {1, 2, 3, 4, 6, 7, 12}:
- Compute per-timestamp scalar |A_k| at the Gainesville lagna (lat=29.65, lon=-82.34) using the same compute_chart and pair_interference machinery as PREREG_001.
- Aggregate to daily means.
- Pearson r against daily SF tide range, n = 18,702 (same as M4).
- Block-bootstrap 95% CI with 30-day blocks, 1000 resamples.

Test labels: K1, K2, K3, K4, K6, K7, K12.

### 2b. Sub-family S — multi-station (6 tests)

Stations and approximate latitudes:
- S_VIZ:  Vishakhapatnam, India (17.7°N, 83.3°E) — UHSLC
- S_CHN:  Chennai, India        (13.1°N, 80.3°E) — UHSLC
- S_KOC:  Kochi, India           (9.9°N, 76.3°E) — UHSLC
- S_MUM:  Mumbai, India         (18.9°N, 72.8°E) — UHSLC
- S_SF:   San Francisco         (37.8°N, 122.5°W) — NOAA CO-OPS (already fetched)
- S_HON:  Honolulu              (21.3°N, 157.9°W) — NOAA CO-OPS

For each station: fetch hourly_height 1973-01-01 through 2024-12-31 if not already present; compute station-local lagna at every 10-min timestamp using station coordinates; compute the same Sun-Moon raw-amplitude reduction (averaged across k ∈ {1,2,3,4,6,7,12}) at that station's lagna; aggregate to daily mean; compute daily tide range from station's hourly_height; Pearson r between station-local-lagna amplitude and station-local tide range.

Block-bootstrap 95% CI with 30-day blocks, 1000 resamples per station.

Document station coverage gaps explicitly per station.

### 2c. Multiple-comparison correction

Holm correction across the combined family of 13 tests (K1..K12 + S_VIZ..S_HON), at family α = 0.05.

A test "survives" only if all three:
- Holm-adjusted p < 0.05
- 95% CI excludes zero
- |r| ≥ 0.05

### 2d. Sample window and exclusions

1973-01-01 through 2024-12-31. Honor known archive gaps. For multi-station tests, exclude rows where the local station has no observation; do not impute.

## 3. Outcome interpretation (locked)

### 3a. k-decomposition outcome interpretation

- **K2 dominates and other k near zero:** consistent with M2/S2 standard tidal physics. M4 r is mostly known mechanism.
- **K2 large but multiple other k also survive |r| ≥ 0.05:** signal extends beyond standard tidal physics. Higher k harmonics contributing requires non-trivial mechanism.
- **K2 not dominant:** the M4 r is *not* primarily standard tidal physics. The reduction is capturing something else.

### 3b. Multi-station outcome interpretation

- **All stations survive at similar r magnitudes (within ±0.05 of each other):** generic Sun-Moon geometry, no lagna-specificity. The Gainesville lagna in PREREG_001 was doing no work.
- **r magnitudes track latitude in a structured way (e.g., increasing or decreasing monotonically with |lat|):** the lagna-coupling hypothesis is supported. Station-specific lagna geometry is the operative variable.
- **Indic-cluster (S_VIZ, S_CHN, S_KOC, S_MUM) shows systematically different r magnitudes than Pacific control (S_SF, S_HON):** geographic structure exists, but cluster-difference does NOT establish classical-significance coupling without basin-physics-controlled follow-ups (see §3d). This outcome supports geographic-structure existence but is interpretively ambiguous between (i) genuine field-amplification at classically-significant locations, (ii) Indian Ocean basin tidal physics differing from Pacific in ways that interact with Sun-Moon geometry, and (iii) data-quality artifacts (UHSLC vs NOAA coverage differences).
- **Some stations survive and others don't, with no clear latitude or cluster pattern:** mixed result. Probably points at coverage-quality differences across stations rather than a real geographic pattern.

### 3c. Combined hypothesis discrimination

| Sub-family K result          | Sub-family S result                         | Hypothesis supported           |
| ---------------------------- | ------------------------------------------- | ------------------------------ |
| k=2 dominates                | uniform across stations                     | A — known tidal physics only   |
| k=2 dominates                | latitude-structured                         | B — partial novelty            |
| Multiple k survive           | uniform across stations                     | B — partial novelty            |
| Multiple k survive           | latitude-structured                         | C — lagna-coupled wave-field   |
| Any                          | Indic-cluster vs Pacific differs            | D — geographic structure of unknown origin (requires basin-physics-controlled follow-up before interpretation) |

### 3d. Required follow-up if outcome D obtains

If sub-family S produces an Indic-cluster vs Pacific cluster difference, no claim about classical-significance coupling can be made without a follow-up pre-registration that includes:
- Indian Ocean basin stations OUTSIDE classically-significant regions as additional controls
- Pacific basin stations IN classically-significant regions (e.g., Hawaiian sites with Polynesian sacred geography) as additional controls
- Basin-physics control via independent tidal-constituent decomposition

This requirement is locked in this pre-registration to prevent post-hoc interpretation of cluster-difference results as classical-coupling evidence.

## 4. What the M4 multi-decade result showed

Brief summary, for context: M4 was the only survivor of PREREG_001's M1-M4 family. r = +0.1945, n = 18,702, stable across solar-cycle phases. The result motivates this follow-up but is not used as a power prior in any specific way; the locked test designs in §2 are not informed by M4's specific r magnitude.

## 5. Possible meta-outcomes

- **All 13 tests pass:** strong support for hypothesis C. Likely publishable.
- **K subset only passes (not S):** k-distribution informs novel-physics question. Publishable as bounded methodological finding.
- **S subset only passes (not K):** lagna-coupling supported but mechanism question open.
- **Cluster-difference result (outcome D):** geographic-structure existence supported, classical-significance interpretation deferred to follow-up prereg.
- **Subset of each passes:** partial result requiring interpretation.
- **No tests pass:** M4 was a chance fluctuation despite large n and solar-cycle stability. The hypothesis at this reduction is rejected.

## 6. Deviation clause

Any analysis run that deviates from the locked design in §2 must be reported as exploratory and not contribute to the confirmatory claim. In particular, the following adjustments are expressly disallowed without committing a new pre-registration first:

- Choosing a different k subset after seeing per-k results
- Excluding any station from the analysis after seeing that station's r
- Adjusting block-bootstrap parameters based on observed results
- Adding additional stations or harmonics beyond those specified above
- Redefining "lagna" or modifying the per-station amplitude computation
- Substituting a different effect-size threshold or correction method
- Interpreting cluster-difference results (§3b last entry) as classical-significance coupling without the §3d follow-up

Replication of the test on additional independent data (a new station, new years of data) would be a new pre-registration — not a deviation.

## 7. Operational notes (non-locking)

These are implementation guidance and do not constitute design choices:

- Multi-station tide data fetch will use UHSLC for the Indian stations (Vishakhapatnam, Chennai, Kochi, Mumbai) and NOAA CO-OPS for the Pacific stations (San Francisco already fetched, Honolulu new).
- UHSLC API: https://uhslc.soest.hawaii.edu/data/ — Research Quality Dataset (RQD) provides hourly-resolution multi-decade records.
- Per-station lagna computation requires station latitude and longitude as inputs to compute_chart; otherwise identical to the Gainesville-lagna computation in build_sun_moon_field_multidecade.py.
- k-decomposition is structurally trivial given the existing pair-interference machinery — instead of averaging across k, retain per-k values and aggregate per-test.
- Wall-clock estimate: multi-station fetch ~30-60 min; per-station amplitude builds ~5 min each (panchanga grid already exists from PREREG_001 work, only the lagna at each station needs recomputation).

## 8. Signature

Date of pre-registration: 2026-05-08
Lock-marker: first commit on this file path, recoverable via `git log --follow`.
This pre-registration is independent of and does not modify PREREG_001 (locked at b3bad8e). M4's result motivated this follow-up but is not used as a parameter in any locked test specification.
