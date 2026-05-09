# Multi-pair mode-phase exploratory plots — Gainesville lagna, 2025

**Status:** exploratory visualization. NOT pre-registered, NO statistical tests.
Builds on `research/geosolar/exploratory/mode_decomposition_2025/` (single-pair
Sun-Moon) by extending to 10 graha pairs.

## Pairs

- `sun_moon`: Sun–Moon
- `sun_mars`: Sun–Mars
- `sun_mercury`: Sun–Mercury
- `sun_venus`: Sun–Venus
- `sun_jupiter`: Sun–Jupiter
- `sun_saturn`: Sun–Saturn
- `moon_mars`: Moon–Mars
- `moon_mercury`: Moon–Mercury
- `moon_jupiter`: Moon–Jupiter
- `jupiter_saturn`: Jupiter–Saturn

## Dataset

`all_pairs_modes_2025.parquet` — 52,560 rows × ~180 cols at 10-min cadence.
Per pair, columns include `re_k{1..12}`, `im_k{1..12}`, `magnetic`,
`dielectric`, `mode_ratio`, `mode_phase`, `synodic_phase`.

## Plots

- **mode_phase_polar_overlay.png** — polar plot, 10 pairs as different-colored
  point clouds. θ = mode_phase = atan2(dielectric, magnetic). r = mode_ratio.
  Look for: do different pairs occupy different regions?
- **mode_phase_vs_synodic_phase_grid.png** — 3×4 small multiples, one panel
  per pair, plotting mode_phase vs synodic_phase. Look for: does mode_phase
  rotate monotonically with synodic phase, or in some more complex pattern?
- **mode_ratio_distribution_by_pair.png** — boxplot per pair. Does mode mix
  vary systematically across pair identity?
- **mode_ratio_correlation_matrix.png** — pairwise Pearson correlations
  between the 10 pairs' mode_ratio time series. Synchronized? anti-correlated?
- **multi_pair_simultaneous_alignment.png** — for each timestamp, count of
  pairs with mode_ratio in extreme regime (< 0.30 or > 0.70). Time series
  + histogram. Look for: moments when many pairs simultaneously align.

## Caveat

The pair magnitude `|Z_k|` at any target reduces to `2|cos(k(β-α)/2)|` by
closed-form identity (target-invariant, independent of lagna). The mode
decomposition into Re/Im is what carries target-dependent information.
These plots therefore reflect the lagna-coupled component geometry, not
the pair-magnitude (which is a global function of pair separation).
