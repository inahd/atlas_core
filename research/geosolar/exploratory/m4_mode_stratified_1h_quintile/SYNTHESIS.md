# Sub-daily mode-stratified M4 reanalysis, v2 — 1-hour quintile-cut SYNTHESIS

**Status:** EXPLORATORY. Not pre-registered. Not citable as confirmatory.

Date generated: 2026-05-08

## What this is

Re-run of the 6-hour mode-stratified M4 reanalysis after that pass's
stratification cuts (0.40 / 0.60) collapsed 99.97% of windows into one
bin (the 6-hour-mean mode_ratio range was [0.39, 0.60]). Two changes:

1. **1-hour cadence** (instead of 6-hour aggregation) for the
   stratification variable. At 1-hour, lagna sweeps only 15° per
   sample vs 90° per 6h, so per-hour mode_ratio retains ~3× wider
   variation.
2. **Data-driven quintile cuts** (bottom 20% / middle 60% / top 20%)
   computed from the actual 1-hour mode_ratio distribution, instead of
   the fixed 0.40/0.60 cuts that the data didn't span at 6h.

Methodological note (necessary, since SF tide gauge is hourly and
max-min within a 1-hour window is degenerate): **M4 amplitude at
each hourly timestamp is computed as a 6-hour-centered rolling
max − min** of water_level — i.e., M4_amp(t) = max(wl[t−3h..t+3h]) −
min(wl[t−3h..t+3h]). This preserves the sub-daily-tide-range semantics
of the predictand while letting the stratification variable mode_ratio
vary at full hourly resolution.

## Diagnostics (mode_ratio at 1-hour cadence)

- Range: **[0.0000, 0.7533]**
- Std:  **0.1093**  (3.21× wider than 6h's 0.034)
- 20th percentile cut: **q20 = 0.4451**
- 80th percentile cut: **q80 = 0.5749**

## Sample sizes and per-quintile results

| Quintile | n hourly samples | Pearson r | 95% bootstrap CI | raw p |
|---|---:|---:|---|---:|
| bottom_quintile | 89,734 | +0.0433 | [+0.023, +0.067] | 1.81e-38 |
| middle | 269,202 | -0.0271 | [-0.041, -0.014] | 4.53e-45 |
| top_quintile | 89,734 | -0.0380 | [-0.058, -0.019] | 4.72e-30 |
| **POOLED** | 448,670 | -0.0169 | [-0.027, -0.005] | 1.34e-29 |

Block-bootstrap CI uses 30-day blocks (= 720 hourly samples), 1,000 resamples.

## Top vs bottom quintile comparison

- top - bottom r difference: **-0.0813**
- 95% CIs: **DO NOT OVERLAP**

The CIs of the bottom and top quintile r-values do NOT overlap,
meaning the strata are distinguishable at the 95% level under
this design. **This is suggestive but not confirmatory** — the
test was performed once, on the same year-window PREREG_001 used,
after the hypothesis was formed. A pre-registered held-out
replication is required before treating this as a finding.

## Plots

- `m4_vs_sun_moon_by_mode_quintile_1h.png` — three panels (bottom /
  middle / top quintile), scatter of M4 amplitude vs Sun-Moon
  separation with regression line.
- `mode_ratio_distribution_1h_windows.png` — histogram of 1-hour
  mode_ratio with q20 and q80 cuts marked.
- `correlation_by_mode_quintile_with_bootstrap.png` — bar chart of
  per-quintile r with 95% block-bootstrap CI; pooled r as dashed line.
- `m4_residual_after_standard_tidal_by_quintile.png` — residual after
  pooled linear fit, stratified by quintile.

## ⚠ Major confound — the apparent stratum effect may be selection bias

`mode_ratio` at the lagna is a function of the lagna-Sun-Moon
geometry, which itself depends on the Sun-Moon angular separation
(the predictor). **Stratifying by mode_ratio therefore implicitly
stratifies by the predictor's own distribution**. The per-stratum
Pearson r conflates two different things:

1. *Genuine mode-mediated moderation* of the M4 ↔ Sun-Moon-separation
   relationship — what the test was intended to measure.
2. *Selection bias* — different strata over-sample different
   sub-ranges of Sun-Moon separation, and the underlying M4 ↔
   separation relationship is non-monotonic (roughly |cos(2·sep)|,
   with maxima at conjunction/opposition and minima at quadrature).
   A linear Pearson r computed on different sub-ranges of a non-
   monotonic curve will give different values *by construction*,
   even with no true moderation effect.

The pooled r ≈ 0 (−0.017) is **exactly what you'd expect** from a
non-monotonic 4-cycles-per-360° spring/neap envelope averaged over
the full angular range. The per-stratum r diverging from zero in
opposite directions is **exactly what selection on a confounded
stratification variable produces**.

**This means the apparent "non-overlapping CIs" finding is NOT clean
evidence of mode-mediated moderation.** It is consistent with two
hypotheses simultaneously: (a) genuine moderation, or (b) an artifact
of stratifying by a variable that's coupled to the predictor.

To distinguish (a) from (b), the test should use one of:

- **Circular / harmonic predictor**: `|cos(2·separation)|` (the
  spring/neap envelope) instead of raw separation, then test whether
  the relationship between this envelope and M4_amp differs across
  mode strata.
- **Conditional regression**: regress M4_amp on (separation, mode_ratio,
  separation × mode_ratio), test whether the interaction term is
  significant after controlling for the main effects.
- **Stratify by a variable independent of Sun-Moon geometry**: e.g.,
  solar wind speed, geomagnetic Kp index, season, or hour-of-day.
  Then check whether M4 ↔ separation differs across those strata.

The current result is logged as a diagnostic — useful to surface that
the variable space has structure — but the structure does not support
the framework prediction without the additional controls above.

## Other caveats

- Single-window test on data already used in PREREG_001; cannot serve
  as an independent confirmatory test no matter how clean the strata
  separate.
- 6-hour-centered rolling M4_amp introduces autocorrelation in the
  predictand at hourly cadence (consecutive hours share 5 of 6 samples
  in the rolling window). Block-bootstrap with 30-day blocks is
  intended to absorb this.
- Quintile cuts are post hoc to the data — the dataset itself
  defines the strata boundaries. Acceptable for exploratory use but
  should be locked in advance for any confirmatory replication.

## If results are suggestive: follow-up design

If the top-vs-bottom comparison shows non-overlapping CIs, a
confirmatory follow-up should:
- Pre-register with: lagna location, predictand cadence, predictor
  definition, stratification cuts (specified in advance, not
  data-driven at execution time), and survival criterion.
- Use a held-out gauge (e.g. Honolulu, Boston, or other multi-decade
  NOAA gauge) AND/OR held-out years.
- Use circular-statistics-aware predictor (harmonic regression on
  Sun-Moon angle, not linear Pearson).

*Total wall: 20.7s*