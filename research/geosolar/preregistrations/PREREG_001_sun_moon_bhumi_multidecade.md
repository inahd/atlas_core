# PREREG-001 — Sun-Moon Wave-Field × Bhūmi-Layers (Multi-Decade Confirmatory Test)

## 1. Preamble

This document **locks the analysis design** for a confirmatory test of the Sun-Moon wave-field amplitude → bhūmi-layer correspondence hypothesis on the multi-decade geosolar archive (1973–2024).

The locking commit for this pre-registration is the most recent commit affecting this file path in git history. Verify with: `git log --follow research/geosolar/preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md`. The first commit on that file is the lock; subsequent commits (if any) must be reported as deviations under the deviation clause above.

Any deviation from the design specified below — different reduction, different test family, different correction, different stratification, different effect-size threshold, different sample window — must be reported as **exploratory** and labeled as such in the resulting analysis document. Such deviations do not invalidate the confirmatory result, but they do not contribute to the confirmatory claim either (see §6).

## 2. Hypothesis

The Sun-Moon raw-amplitude wave-field state at the lagna (Gainesville coordinates, lat = 29.65, lon = −82.34) at any timestamp predicts the bhūmi-layer measurements at that timestamp, with **positive** correlation expected for ring-current intensity (Dst) and tide range, and **direction unspecified** for Kp index and seismic count.

## 3. Pre-Specified Test Design (LOCKED)

### 3.1 Reduction

For each test timestamp `t`:

1. Sun longitude `sun_long(t)` and Moon longitude `moon_long(t)` computed via Swiss Ephemeris (Lahiri sidereal ayanāṃśa).
2. Lagna longitude `lagna_long(t)` computed via `compute_chart(dt_utc=t, lat=29.65, lon=-82.34)` from `npu_engine.jyotisha_engine` (Lahiri sidereal, whole-sign house system).
3. For each `k ∈ {1, 2, 3, 4, 6, 7, 12}`:

       A_k(t) = cos(k · (lagna_long(t) − sun_long(t))) + cos(k · (lagna_long(t) − moon_long(t)))

   (This is exactly `compute_pair_interference(sun_long, moon_long, lagna_long, k)` from `npu_engine.jyotisha_engine`.)
4. The locked scalar is

       sun_moon_amplitude(t) = mean over k of |A_k(t)|

   range [0, 2].

This reduction is **identical** to the 2025 exploratory reduction at `research/geosolar/pilot_2025/scripts/build_sun_moon_field.py`. Re-implementation is acceptable but the formula and inputs are locked.

### 3.2 Test Family

Four Pearson correlations:

| Test | Response | Predictor | Cadence |
|---|---|---|---|
| **M1** | Kp index | sun_moon_amplitude | 3-hourly |
| **M2** | Dst (nT) | sun_moon_amplitude | hourly |
| **M3** | Daily M≥4 seismic event count | daily-mean sun_moon_amplitude | daily |
| **M4** | Daily tide range (m) | daily-mean sun_moon_amplitude | daily |

Pearson r computed via `scipy.stats.pearsonr` (or numerically equivalent). Daily-mean `sun_moon_amplitude` is the arithmetic mean of all 10-min values within a UTC calendar day.

### 3.3 Multiple-Comparison Correction

Holm-Bonferroni step-down across the family of m = 4 tests. Family α = 0.05.

### 3.4 Autocorrelation Handling

- **M1 and M2 (high-cadence Kp and Dst):** primary p-value is the **block-permutation p** with 30-day blocks, 1,000 resamples, computed by shuffling block ordering of the response series against the unchanged `sun_moon_amplitude` series and counting `|r_perm| ≥ |r_obs|`. The scipy/Pearson p-value is reported alongside but is **not** the primary p for these tests.
- **M3 and M4 (daily aggregates):** primary p-value is the standard `scipy.stats.pearsonr` p, with a 95% confidence interval computed via moving-block bootstrap (block size = 30 days, 1,000 resamples).

### 3.5 Survival Criterion

A test is considered to **survive** if and only if **both**:

1. The Holm-adjusted (within-family m = 4) primary p-value is < 0.05, AND
2. The 95% CI on Pearson r excludes zero.

Both conditions must hold simultaneously. Either alone is insufficient.

### 3.6 Solar-Cycle Stratification

Each test is additionally reported stratified by solar cycle phase: **minimum**, **ascending**, **maximum**, **descending**. The phase boundaries are determined from the monthly smoothed sunspot number against the standard SILSO catalog (sidc.be), using the published cycle minimum/maximum dates as anchors:

- Cycle 21: 1976-03 (min) → 1979-12 (max) → 1986-09 (min)
- Cycle 22: 1986-09 (min) → 1989-07 (max) → 1996-08 (min)
- Cycle 23: 1996-08 (min) → 2001-11 (max) → 2008-12 (min)
- Cycle 24: 2008-12 (min) → 2014-04 (max) → 2019-12 (min)
- Cycle 25: 2019-12 (min) → 2024-10 (max, provisional) → ongoing

For each cycle, "ascending" is min→max, "descending" is max→next-min, with the inflection months assigned to "max"/"min" categories respectively. Stratified r is reported as a four-row breakdown alongside the pooled r. The **pooled multi-decade result is the headline**; stratification is descriptive context, not a separate confirmatory claim.

### 3.7 Effect-Size Threshold

For confirmation, |r| must additionally satisfy

       |r_pooled| ≥ 0.05

This is **deliberately below** the conventional 0.1 small-effect threshold, because multi-decade n is large enough to detect smaller effects than the 2025 pilot could; but it is a guard against trivial-magnitude noise being labeled significant simply by virtue of n.

### 3.8 Sample Window

- 1973-01-01 00:00:00 UTC through 2024-12-31 23:50:00 UTC inclusive.
- 10-min cadence for the predictor `sun_moon_amplitude` (computed on the same 10-min ephemeris grid as the 2025 pilot, extended).
- For each response variable, the native cadence is used (Kp 3-hourly, Dst hourly, seismic event-time, tide hourly), joined to the predictor grid via `pd.merge_asof(..., direction='nearest')`.
- Rows flagged in `datasets/geosolar/archive/BULK_REPORT_1973_2024.md` as missing or station outage are **excluded**. The exclusion list is taken from the bulk report at the time of analysis; no row-by-row response-conditional cleaning is permitted.

## 4. What the 2025 Exploratory Result Showed

The 2025 pilot (`research/geosolar/pilot_2025/SUN_MOON_FIELD_EXPLORATORY_2025.md`) ran the same four-test family at lower n on calendar 2025 only, **after** the pre-specified zodiacal-mean wave-field test (`WAVE_FIELD_ANALYSIS_2025.md`) returned a clean null. The reduction tested here was chosen *post hoc*, motivated by diagnostic evidence that per-k normalization had compressed variance; the 2025 result is therefore exploratory and is not citable as a finding.

Headline 2025 numbers (for power/scale calibration only):

- **W4'** Hydrosphere (daily tide range): r = +0.212, Holm-adjusted p = 1.4 × 10⁻⁴, 95% CI [+0.065, +0.352].
- **W2'** Ring current (Dst): r = +0.113, Holm-adjusted p = 8.9 × 10⁻²⁶, 95% CI [+0.068, +0.166].
- **W1'** Magnetosphere (Kp): apparent r = −0.068 with raw p = 2.2 × 10⁻⁴, but block-permutation p = 0.42 → **disqualified** by autocorrelation-aware test.
- **W3'** Lithosphere (daily seismic count): r = −0.054, p = 0.30. Null.

These 2025 numbers are used ONLY as a power/scale prior for the multi-decade design. They are not, individually or collectively, the confirmatory finding.

## 5. Possible Outcomes and Their Interpretation (LOCKED)

The following outcome interpretations are locked in advance, before multi-decade data is loaded:

### 5a. All four of M1–M4 survive at multi-decade scale with |r| ≥ 0.05

**Interpretation:** Confirmatory finding for the bhūmi-stratification hypothesis at this reduction. The Sun-Moon raw-amplitude wave-field at the lagna predicts bhūmi-layer measurements differentially. Becomes the basis for a paper. Solar-cycle stratification reported as descriptive context.

### 5b. Subset of M1–M4 survive — most likely scenario given 2025 priors

**Interpretation:** Partial confirmation. The specific tests that survive **become the finding** at the layer-level granularity at which they survive; tests that don't survive are reported as nulls at multi-decade scale. The 2025 result flagged M2 (Dst) and M4 (tide range) as the most likely candidates; if either or both survive, they survive on their own merits. M1 (Kp) and M3 (seismic) entering the survival set would be especially noteworthy because the 2025 result did not predict them.

### 5c. None of M1–M4 survive at multi-decade scale

**Interpretation:** The 2025 exploratory result was a chance fluctuation at lower n. The hypothesis at this reduction (Sun-Moon raw-amplitude lagna scalar) is **rejected**. This is a publishable null. Future work would test alternate reductions (per-graha-pair decomposition, nakshatra-midpoint targets, or non-amplitude derivatives) but each of those would itself need to be pre-registered separately before testing.

### 5d. Effect sizes substantially larger than 2025 priors

**Interpretation:** Investigate methodology before claiming. Multi-decade amplification is plausible (more power, more decades smoothing solar-cycle variation) but a several-fold increase over the 2025 |r| ≥ 0.2 priors should be sanity-checked against:

- solar-cycle confounding (is the apparent effect actually tracking the cycle, with `sun_moon_amplitude` happening to correlate with cycle phase?)
- station-record discontinuities in the response series across decades
- Lahiri ayanāṃśa drift artifacts in the predictor over fifty years

If the sanity checks pass, the larger effect is the finding; if they fail, the finding is reduced or retracted accordingly.

## 6. Deviation Clause

Any analysis run on the 1973–2024 multi-decade data that deviates from the locked design above — including, but not limited to:

- Different reduction or scalar
- Different target (not the lagna) or different lagna location (not Gainesville)
- Different test family or different response variables
- Different multiple-comparison correction or different family α
- Different autocorrelation handling
- Different sample window or different exclusion rules
- Different effect-size threshold or different survival criterion

— **must be reported as exploratory** and labeled as such in the resulting analysis document. Such exploratory analyses do not invalidate the confirmatory result, but they do not contribute to the confirmatory claim either. The confirmatory claim is whatever the M1–M4 survival pattern is, as specified above, no more and no less.

## 7. Signature

- **Date of pre-registration (UTC):** 2026-05-08
- **Location:** Atlas Core repository, branch `main`, file `research/geosolar/preregistrations/PREREG_001_sun_moon_bhumi_multidecade.md`
- **Locking commit:** recover from `git log --follow` on this file path (the first commit is the lock; see §1)
- **Author:** inahd (Gainesville, FL)
- **Multi-decade data state at time of pre-registration:** NOT LOADED for analysis. The bulk archive 1973–2024 may exist on disk in `datasets/geosolar/archive/` but no statistical or correlational analysis has been performed against `sun_moon_amplitude` over that window.

The analysis script that runs the locked M1–M4 tests on the multi-decade data **must reference this commit hash directly** in its docstring or header, so that anyone reading the analysis output can verify the pre-registration was committed before the analysis was run, and that no covert design changes occurred between this commit and the analysis commit.
