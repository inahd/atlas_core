# AEF ↔ spring/neap envelope, mode-stratified — SYNTHESIS

**Status:** EXPLORATORY. Not pre-registered. Counterpart to the M4
envelope-mode-stratified test (commit 7847576).

Date: 2026-05-08

## What this is

Framework predicts opposite outcomes for two phenomena:

- **M4** (magnetic-mode rotational/equatorial gravitational tide):
  no mode-coupling. **VERIFIED** in commit 7847576: interaction β = -0.00475,
  OLS p = 0.786, bootstrap CI [-0.022, +0.013], ΔR² = 0.
- **AEF** (dielectric-mode longitudinal/axial atmospheric-electric field):
  mode-coupling SHOULD be present. **THIS test.**

Same predictor (envelope = |cos(2·sep)|), same statistical approach
(interaction regression with controls + block-bootstrap CI), same family
of plots, for direct comparability.

## Data

- Source: PANGAEA 10.1594/PANGAEA.942036, Hungary Széchenyi István Observatory.
- Lagna: Nagycenk, 47.632°N, 16.718°E.
- Predictand: `pg_corr` (corrected hourly potential gradient, V/m).
- Years: 1962–2009.
- Raw rows: 420,768
- After fair-weather filter (precip_era=0, wind_era<8 m/s, RH_era<90%): **95,864** rows (22.8%)

## Versor decomposition diagnostics

- mode_ratio at Hungary lagna: range = [0.0000, 0.7509], std = 0.1093
- Quintile cuts (data-driven): q20 = 0.4446, q80 = 0.5743

## Pooled AEF ↔ envelope correlation

- r = **-0.0021**, 95% CI = [-0.024, +0.020], p = 0.517

## Per-stratum r

| Quintile | n | Pearson r | 95% bootstrap CI | raw p |
|---|---:|---:|---|---:|
| bottom_quintile | 19,173 | -0.0120 | [-0.042, +0.013] | 0.0954 |
| middle | 57,518 | +0.0019 | [-0.020, +0.023] | 0.647 |
| top_quintile | 19,173 | -0.0048 | [-0.027, +0.013] | 0.511 |
| **POOLED** | 95,864 | -0.0021 | [-0.024, +0.020] | 0.517 |

top − bottom = +0.0073, CIs OVERLAP.

## Interaction regression

    pg_corr = β₀ + β₁·envelope_c + β₂·mode_ratio_c + β₃·envelope_c×mode_ratio_c
            + β₄·T_era_c + β₅·wind_era_c + β₆·RH_era_c + β₇·sin(season) + β₈·cos(season) + ε

All non-binary predictors mean-centered. Controls: temperature, wind, humidity
(ERA5 reanalysis), and seasonal harmonics.

| Coefficient | β | SE | t | OLS p |
|---|---:|---:|---:|---:|
| intercept | +106.34751 | 0.21597 | +492.42 | 0 |
| envelope (centered) | +0.05920 | 0.68702 | +0.09 | 0.931 |
| mode_ratio (centered) | -5.02522 | 1.93926 | -2.59 | 0.00956 |
| envelope×mode_ratio | +0.61147 | 6.19666 | +0.10 | 0.921 |
| T_era (centered) | +0.37877 | 0.04632 | +8.18 | 2.93e-16 |
| wind_era (centered) | -11.83890 | 0.15257 | -77.60 | 0 |
| RH_era (centered) | -1.47372 | 0.01834 | -80.33 | 0 |
| season_sin | +5.80174 | 0.32860 | +17.66 | 1.18e-69 |
| season_cos | +38.04760 | 0.55466 | +68.60 | 0 |

- R²(full)        = **0.16454**
- R²(no interaction) = **0.16454**
- ΔR² from interaction = **+0.00000**
- Block-bootstrap 95% CI on interaction β: [-9.16732, +12.09093]
- Interaction CI **INCLUDES** zero
- Block-bootstrap 95% CI on mode_ratio main β: [-8.48088, -1.52739]
- mode_ratio main effect CI **EXCLUDES** zero

## Direct M4 vs AEF comparison

Both phenomena tested with identical methodology — interaction regression of
`{predictand} ~ envelope + mode_ratio + envelope·mode_ratio + controls`.

| Phenomenon | n | interaction β | OLS p | bootstrap 95% CI | ΔR² |
|---|---:|---:|---:|---|---:|
| **M4** (SF tide range, 1973-2024) | 448,670 | -0.00475 | 0.786 | [-0.022, +0.013] | 0.00000 |
| **AEF** (Hungary PG, 1962-2009)    | 95,864 | +0.61147 | 0.921 | [-9.16732, +12.09093] | +0.00000 |

## Honest interpretation

The AEF interaction term is **NOT statistically distinguishable from zero**
(β = +0.61147, bootstrap CI -9.16732 to +12.09093).
Combined with the M4 negative result, **the framework prediction of
differential mode-coupling between magnetic-side (M4) and dielectric-
side (AEF) phenomena is NOT supported by the data**: both phenomena show
a null interaction.

The mode_ratio main effect IS statistically distinguishable from zero
(β = -5.02522, bootstrap CI -8.48088 to -1.52739).
This indicates mode_ratio independently predicts AEF after controlling
for envelope and meteorology — a positive finding for dielectric-mode
coupling at the main-effects level even if the moderation hypothesis
doesn't hold.

## Plots

- `aef_vs_envelope_pooled.png` — basic envelope predictor.
- `aef_vs_envelope_by_mode_quintile.png` — three panels stratified.
- `interaction_regression_AEF_diagnostic.png` — residuals after
  main-effects+controls, by mode_ratio.
- `mode_ratio_vs_aef_marginal.png` — does mode_ratio independently
  predict AEF after controlling for envelope?

## Caveats

- Single-window exploratory test; not pre-registered.
- Quintile cuts data-driven (post hoc), not locked.
- Hungary lagna is the geographic location of the gauge — same lagna
  position used for stratification variable and predictand.
- Fair-weather filter is a literature-standard choice but other
  filter formulations (stricter wind, RH<70, exclude sunrise/sunset, etc.)
  give different sample sizes. Sensitivity to filter choice not yet tested.
- AEF tree-shielding correction is itself uncertain (PANGAEA documents
  this; uncertainty column is in the data). Using `pg_corr` per dataset
  recommendation; a sensitivity check on `pg_uncorr` could show whether
  the correction influences the interaction.

*Total wall: 17.8s*