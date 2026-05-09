# PREREG_006 — Multi-station Schumann resonance replication of dielectric-register mode-coupling

**Pre-registration date:** 2026-05-08
**Lock-marker:** the first commit on this file path. Verify with
`git log --follow research/geosolar/preregistrations/PREREG_006_schumann_multi_station_dielectric_replication.md`.
Subsequent commits are deviations under §6.

**Numbering note:**
- PREREG_003: reserved for atmospheric-electric-field work; the
  exploratory AEF result at commit 0099e18 was tested before the
  prereg was filed (process disclosure in §1) and consequently
  retains exploratory status. PREREG_003 number remains formally
  reserved for a fully pre-registered AEF test if pursued.
- PREREG_004: abandoned (Mercury-mediator hypothesis on data already
  used to generate the hypothesis).
- PREREG_005: drafted earlier in this session at one point but
  renumbered here to PREREG_006 per the user's preference; that
  number was never committed and is treated as never-used.
- PREREG_006: this document.

## 1. Provenance and disclosure

### 1.1 Hypothesis-formation history (honest disclosure)

The hypothesis tested here was **structurally articulated in
framework memory** (Atlas's persistent memory file
`feedback_architecture.md`, line 15-16) **on 2026-05-08, before any
of the dielectric-register physical data targeted in this prereg
was inspected at the level of mode-coupling structure**.

The framework prediction:
- Magnetic-register bhumi-layer indicators (ring-current Dst, daily
  tide range driven by gravity, daily M≥4 seismic count): mode-
  coupling absent or noise-level.
- Dielectric-register bhumi-layer indicators (atmospheric electric
  field, Schumann resonance amplitude, ionospheric potential):
  mode-coupling present.

This is the prediction being tested in PREREG_006.

### 1.2 Process disclosure: prior tests and ordering

Two prior tests on related data were executed by the agent (Claude
Opus 4.7 [1M context]) BEFORE pre-registration documents were
filed:

- **Commit 7847576 (M4 tide range, San Francisco gauge, magnetic-
  side, 1973-2024)**: interaction null AND main effect of mode_ratio
  significant in absence of meteorological controls. Direction-
  ambiguous because no meteorological controls were applied; the M4
  mode_ratio main effect could be confounded with seasonality.
- **Commit 0099e18 (Hungary AEF, dielectric-side, 1962-2009)**:
  interaction null AND mode_ratio main effect significant after
  meteorological controls (T, wind, RH, season). β = -5.025,
  bootstrap CI [-8.48, -1.53], OLS p = 0.0096. Direction:
  high-mode_ratio (dielectric-dominant) periods predicted lower
  AEF.

The framework prediction articulated in memory was identical to
what would have been formally pre-registered. The document-order
issue does not affect what was predicted, only when the prediction
document was filed. The two prior tests therefore retain
exploratory status on their respective datasets.

This prereg locks **before** the multi-station Williams Zenodo
Schumann dataset is inspected at the level of mode-coupling
structure, providing an actually-held-out replication target.

### 1.3 What "not inspected" means precisely

The Williams Zenodo 4276361 multi-station Schumann dataset has
been:
- Identified in the dielectric-mode pre-flight (commit e9329c8,
  access_report.md) as accessible.
- Sample-fetched: NCK_EZ.txt (Nagycenk Hungary, 1996-1999, 7.8 KB)
  was downloaded to verify access. Its column structure and
  monthly-diurnal-averaging format were inspected. **Its mode-
  coupling structure was NOT inspected at any level.**
- The other 5 station files (ALB, BOU, ESK, HRN, RI files) have
  not been downloaded yet. They will be downloaded as part of
  PREREG_006 execution.

Both the test author (Claude Opus 4.7 [1M context]) and the user
(inahd) agree to honor the boundary that no mode-coupling analysis
has been or will be performed on these files between this prereg
lock and the execution session.

## 2. Hypothesis (locked)

**Primary**: Mode_ratio at the station-local lagna predicts Schumann
resonance amplitude at that station, observable as a non-zero main
effect on amplitude after controlling for diurnal, seasonal, and
station-specific variation. Direction prior: negative (high
mode_ratio → lower amplitude), matching the AEF exploratory
direction.

**Secondary**: The mode_ratio × envelope interaction is null
(predicted from M4 + AEF priors).

**Geographic projection-equivalence requirement**: The dielectric-
register coupling claim should hold at *multiple geographically
diverse lagnas*. Single-station support is insufficient.

## 3. Pre-specified test design (locked)

### 3.1 Source data

**Primary source**: Williams et al. multi-station Schumann
resonance dataset, Zenodo DOI [10.5281/zenodo.4276361](https://zenodo.org/records/4276361)
(CC-BY, public, file URLs documented in
`research/geosolar/dielectric_mode_archives/access_report.md`).

The dataset contains **monthly-averaged diurnal amplitude profiles**
(NOT timestamp-level time series). Each TSV file is a 24-row × N-month
table where each cell is the mean Schumann amplitude for the named
hour-of-day within the named month, averaged over all years the
station collected data for that month.

**Stations in the actual Williams dataset** (mismatch note: the
user's earlier proposed station list included Mitzpe Ramon,
Hollister, Esrange — these are NOT in Zenodo 4276361. They would
require separate institutional contact and are out of scope for
this prereg):

| Station code | Location | Approx. lat | Approx. lon | Files |
|---|---|---:|---:|---|
| ALB | Alberta, Canada | +54° | -115° | ALB_HEW.txt, ALB_HNS.txt |
| BOU | Boulder Creek, CA, USA | +37° | -122° | BOU_HEW.txt, BOU_HNS.txt |
| ESK | Eskdalemuir, Scotland | +55° | -3° | ESK_HNS.txt |
| HRN | Hornsund, Norway (Spitsbergen) | +77° | +16° | HRN_HEW.txt, HRN_HNS.txt |
| RI  | Rhode Island, USA | +41° | -71° | RI_HEW.txt, RI_HNS.txt |

**NCK exclusion (locked)**: NCK (Nagycenk, Hungary) is geographically
close to the PANGAEA Hungary AEF gauge whose mode_ratio main effect
was the exploratory result motivating this prereg. To preserve a
stricter held-out boundary, **NCK is excluded from the confirmatory
family**. NCK can be re-tested as an exploratory sanity-check
ALONGSIDE the locked test, but cannot contribute to the
confirmatory claim.

**5 stations are included in the locked confirmatory family**:
ALB, BOU, ESK, HRN, RI.

Exact station coordinates will be confirmed against the Williams
station-list documentation at the start of execution; if any
station's true coordinates differ from the table above by more
than 1°, the actual coordinates from the documentation are used,
this is logged, but it is not a deviation.

### 3.2 Predictand and unit of analysis

For each (station, file, month, hour-of-day) record:
- `sr_amplitude` = the cell value from the Williams TSV file.
- For stations with both HEW and HNS components (ALB, BOU, HRN, RI),
  per-(station, month, hour) amplitude = mean(HEW, HNS).
- For ESK (only HNS), use HNS.
- For stations whose components are otherwise asymmetric, the
  available component(s) are averaged.

Unit of analysis = (station, month, hour). Total records ≈
5 stations × ~36-48 months × 24 hours ≈ 4,300 - 5,800.

### 3.3 Predictors

For each (station, month, hour) record, a representative timestamp
is constructed: **15th day of the named month, at the named UTC
hour, in the temporal-center year of the station's coverage**
(e.g., a station covering 2013-2016 has center year 2014;
"January 2013, hour 5" → 2013-01-15 05:00 UTC; "January, hour 5"
averaged across multiple years uses the median year of the
station's window).

Using this timestamp:
- `lagna_long` at the station's geographic coordinates via swisseph
  (Lahiri sidereal, whole-sign).
- `sun_long`, `moon_long` via swisseph.
- For the Sun-Moon pair at the station's lagna, compute
  Z_k for k ∈ {1, 2, 3, 4, 6, 7, 12} per the locked versor
  reduction (post-DEVIATION_001 versor-aware engine, identical to
  M4 / AEF priors).
- `magnetic_component = sum_k |Re(Z_k)|`
- `dielectric_component = sum_k |Im(Z_k)|`
- `mode_ratio = die / (mag + die + ε)`
- `envelope = |cos(2 · sun_moon_separation)|`
- `sun_moon_separation` (raw, for sanity)

### 3.4 Test specification (locked)

**Per-station test** (descriptive, supports criterion 3 below):

For each station s in {ALB, BOU, ESK, HRN, RI}:
- Pool all (month, hour) records for that station:
  24 hours × ~36-48 months ≈ 864-1,152 records per station.
- Fit OLS (predictors mean-centered):
  ```
  sr_amplitude ~ envelope_c + mode_ratio_c + envelope_c × mode_ratio_c
                 + hour_of_day (24 fixed effects)
                 + month (12 fixed effects)
                 + ε
  ```
- Report β_mode_ratio, β_interaction, OLS SE / t / p, and a
  residual block-bootstrap 95% CI on β_mode_ratio (60-record blocks
  ordered by month-then-hour; 1,000 resamples).

**Combined-stations meta-test (the confirmatory test)**:

Pool all 5 stations into one fixed-effects regression
(predictors mean-centered):
  ```
  sr_amplitude ~ envelope_c + mode_ratio_c + envelope_c × mode_ratio_c
                 + station (5 fixed effects)
                 + hour_of_day (24 fixed effects)
                 + month (12 fixed effects)
                 + station × hour_of_day (interaction term:
                                          per-station diurnal pattern)
                 + ε
  ```
- Report pooled β_mode_ratio, β_interaction, with block-bootstrap
  95% CIs (60-record blocks; 1,000 resamples), OLS p, ΔR² from
  adding the interaction.

### 3.5 Effect-size threshold (descriptive, not gating survival)

The user-specified threshold |β_interaction| > 0.02 is **descriptive,
not gating survival**. The threshold is on the raw interaction-
coefficient scale, and its magnitude depends on the units of
envelope (dimensionless [0,1]), mode_ratio (dimensionless [0,1]),
and `sr_amplitude` (a.u. — Williams records in arbitrary units —
see §5 caveat).

The threshold is reported alongside the bootstrap CI for the
interaction coefficient, but the **primary survival criterion is
bootstrap-CI-excludes-zero** (see §3.6). If a future test on
absolute-unit Schumann data (e.g. nT or V/m at the source) wishes
to use a calibrated effect-size threshold, that's a separate prereg.

### 3.6 Survival criterion (locked)

The confirmatory finding requires **all four** of:

1. **Combined-stations β_mode_ratio bootstrap 95% CI excludes zero**
   (the main effect — direct replication of the AEF exploratory
   finding at multiple lagnas).
2. **Combined-stations β_mode_ratio sign matches AEF prior**
   (negative, high mode_ratio → lower amplitude — one-tailed
   directional prior). Sign-flipped result counts as deviation,
   not confirmation; reported but does not satisfy criterion 2.
3. **At least 3 of 5 stations** independently show β_mode_ratio
   bootstrap 95% CI excluding zero in the same direction as the
   pooled result (geographic projection-equivalence requirement;
    3/5 = 60% threshold, scaled from "4 of 6" earlier draft to
   match the same approximate proportional bar).
4. **Combined-stations β_interaction bootstrap 95% CI includes zero**
   (interaction null, replicating the M4 + AEF prior pattern). If
   the interaction CI excludes zero, this is a new finding and
   triggers outcome 4e below regardless of criteria 1-3.

If criteria 1, 2, 4 hold but 3 fails: weak confirmation (effect
present but not robustly geographic). Reported as suggestive, not
confirmatory.

### 3.7 Random seed

`numpy.random.default_rng(20260508)`.

### 3.8 Data acquisition prerequisite

Before execution:

- All 5 station file groups (ALB, BOU, ESK, HRN, RI) must be
  successfully fetched from Zenodo 4276361. Failure of any station's
  fetch invalidates the primary test on that station; if more than
  1 of 5 stations' files fail to fetch, the prereg's combined-stations
  test cannot meet criterion 3 (which requires ≥3 of 5 individually-
  passing stations) and the execution session reports data-acquisition
  failure rather than running a partial test.

### 3.9 Sample window

Each station's native coverage in the Williams dataset is fully
used. Approximate windows:
- ALB, BOU, ESK, HRN, RI: ~2013-2016
- (Confirmed at execution from each file's column headers.)

## 4. Possible outcomes (locked)

### 4a. Confirmatory finding

All four criteria 1-4 of §3.6 satisfied.

**Interpretation**: Multi-station replication of the dielectric-
register mode-coupling main effect first observed exploratorily at
Hungary AEF. Combined with the M4 negative result, the framework's
broader prediction of differential mode-coupling between magnetic-
side and dielectric-side bhumi-layer indicators gains held-out
support. Becomes the basis for a paper.

### 4b. Pooled effect, but < 3 stations individually meet criterion

Criteria 1, 2, 4 satisfied; criterion 3 fails.

**Interpretation**: Weak confirmation. Effect is present in pooled
data but not robustly geographic — could be driven by 1-2 stations.
Reported as suggestive, not confirmatory.

### 4c. Pooled null

Criterion 1 fails (β_mode_ratio CI includes zero in combined-
stations regression).

**Interpretation**: The Hungary AEF mode_ratio main effect does
not replicate to multi-station Schumann data. The dielectric-
register coupling claim is not supported beyond the single-location
AEF exploratory result. Treated as a publishable null.

### 4d. Pooled effect with sign-flipped from AEF prior

Criterion 1 satisfied but criterion 2 fails (β_mode_ratio > 0,
opposite sign from AEF).

**Interpretation**: Deviation from the AEF prior. A sign flip
across two dielectric-register indicators is itself a substantive
finding requiring framework reconsideration before further testing.

### 4e. Interaction term excludes zero

Criterion 4 fails — combined-stations interaction CI excludes zero.

**Interpretation**: New finding inconsistent with both M4 and AEF
priors. The moderation hypothesis was null in two prior tests but
non-null here. Reported with diagnostic care; would suggest the
moderation pattern is data-dependent in ways the framework needs
to account for.

## 5. Deviation clause

Any departure from §3 is a deviation:

- Different stations (adding NCK or institutionally-acquired
  Hylaty / Mitzpe Ramon / other archives to this confirmatory
  family, dropping any of the 5 locked stations)
- Different test specification (different fixed effects, different
  interaction terms, different bootstrap parameters, different
  number of resamples, different block size)
- Different survival criterion (changing thresholds, dropping any
  of the 4 criteria, switching from one-tailed to two-tailed sign
  match)
- Different effect-size threshold (the |β_interaction| > 0.02
  threshold is descriptive per §3.5, not gating; promoting it to
  gating would be a deviation)
- Different correction method or significance threshold
- Different unit of analysis
- **Inspection of mode_ratio ↔ Schumann-amplitude relationship at
  any of the 5 locked stations between this prereg lock and the
  execution session.** Including: visual inspection of correlation
  matrices, per-station scatter plots, regression fits, summary
  statistics computed across the predictor-predictand pair, etc.
  Inspecting station-side amplitude alone (e.g., diurnal-mean SR
  amplitude per month per station) is not forbidden; what is
  forbidden is observing the mode_ratio↔amplitude joint structure
  before execution.
- Different meteorological or other controls beyond the locked
  hour-of-day and month fixed effects (the Williams dataset doesn't
  include per-record meteorological variables; if supplementary met
  data became available and the user wished to add it as a control,
  that change requires a new prereg before execution)

**Williams arbitrary-unit caveat**: the Williams Zenodo files
record amplitudes in arbitrary units (a.u.) per the dataset
documentation. Coefficients estimated against this scale are not
directly comparable to those estimated against absolute-unit
Schumann data (e.g., nT or V/m at the source instrument). The
descriptive |β_interaction| > 0.02 threshold from §3.5 is reported
on the Williams a.u. scale; if the data turns out to be in a units
range where 0.02 is either trivial or unattainable, the threshold
is reported as descriptive and the survival decision proceeds
solely on the bootstrap-CI-excludes-zero criterion (§3.6).

## 6. Operational notes (non-locking)

Implementation guidance for the future execution session:

- Fetch script:
  `research/geosolar/exploratory/schumann_multi_station/fetch_williams_data.py`
  (downloads all 6 station file groups from Zenodo 4276361).
- Analysis script:
  `research/geosolar/exploratory/schumann_multi_station/run_prereg_006.py`.
- Output:
  `research/geosolar/exploratory/schumann_multi_station/PREREG_006_RESULT.md`
  with per-station table, combined-stations table, pooled β with
  bootstrap CI / sign / criterion-by-criterion survival decision,
  and four diagnostic plots:
  - mode_ratio_vs_amplitude_per_station.png (6 panels, one per
    station)
  - per_station_beta_mode_ratio_with_CI.png (forest plot)
  - combined_regression_diagnostic.png (residuals, fitted values)
  - sign_consistency_check.png (β_mode_ratio sign per station with
    pooled result overlay)
- Wall-clock estimate: <5 minutes (fetches small, ephemeris fast,
  bootstrap on n≈6,000 negligible).

## 7. Signature

Date: 2026-05-08
Author: inahd (test specification, hypothesis articulation, survival
        threshold) + Claude Opus 4.7 [1M context] (formalization,
        held-out boundary enforcement, station list reconciliation,
        deviation clause)
Lock-marker: first commit on this file path, recoverable via
`git log --follow research/geosolar/preregistrations/PREREG_006_schumann_multi_station_dielectric_replication.md`.

This pre-registration is independent of and does not modify
PREREG_001 (locked b3bad8e), PREREG_002 (retired by DEVIATION_001),
or any future PREREG_003. It tests a hypothesis structurally
articulated in framework memory before any of the targeted Williams
multi-station Schumann data was inspected at the level of
mode-coupling structure.

The actual analysis (PREREG_006 execution) is a subsequent session,
on a clean process where the executor commits to honoring the
held-out boundary documented in §1.3 and §5.
