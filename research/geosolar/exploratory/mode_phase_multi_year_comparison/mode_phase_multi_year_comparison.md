# Multi-year mode-phase comparison — 2024 / 2025 / 2026

Cross-year comparison of pair–pair correlation structure of the
versor-decomposed mode_ratio time series at the Gainesville lagna.
Exploratory only. Generated 2026-05-08.

## Datasets

| Year | Source parquet | Rows | Coverage |
|---|---|---:|---|
| 2024 | all_pairs_modes_2024.parquet | 52,704 | full year (leap year) |
| 2025 | all_pairs_modes_2025.parquet | 52,560 | full year |
| 2026 | all_pairs_modes_2026.parquet | 34,128 | 2026-05-09 → 2026-12-31 (partial) |

## Mediator-strength T(m) per graha, by year

Mean off-diagonal correlation across pair-pair matrix entries that
touch at least one pair containing the named graha. Higher values
indicate that pairs containing that graha are more correlated with
the rest of the system.

| Graha | k pairs | T(m) 2024 | T(m) 2025 | T(m) 2026 | Δ 2024→2025 | Δ 2025→2026 |
|---|---:|---:|---:|---:|---:|---:|
| **Sun** | 6 | +0.066 | +0.062 | +0.048 | -0.004 | -0.014 |
| **Moon** | 4 | +0.048 | +0.042 | +0.052 | -0.006 | +0.010 |
| **Mars** | 2 | +0.052 | +0.031 | +0.029 | -0.021 | -0.002 |
| **Mercury** | 2 | +0.089 | +0.096 | +0.082 | +0.007 | -0.014 |
| **Venus** | 1 | +0.086 | +0.075 | +0.024 | -0.012 | -0.051 |
| **Jupiter** | 3 | +0.040 | +0.021 | +0.051 | -0.019 | +0.030 |
| **Saturn** | 2 | +0.034 | +0.050 | +0.002 | +0.016 | -0.048 |

## Top-10 strongest |off-diagonal correlation| per year

### 2024

| Pair A | Pair B | r |
|---|---|---:|
| sun_moon | moon_mercury | +0.350 |
| sun_mercury | sun_venus | +0.337 |
| sun_mars | sun_venus | +0.178 |
| sun_mars | sun_mercury | +0.169 |
| sun_mars | sun_jupiter | +0.131 |
| moon_mars | moon_jupiter | +0.122 |
| sun_moon | sun_mercury | +0.119 |
| sun_mercury | moon_mercury | +0.118 |
| sun_mercury | sun_jupiter | +0.116 |
| sun_saturn | jupiter_saturn | +0.101 |

### 2025

| Pair A | Pair B | r |
|---|---|---:|
| sun_moon | moon_mercury | +0.351 |
| sun_mercury | sun_venus | +0.274 |
| sun_venus | sun_saturn | +0.259 |
| sun_mars | sun_mercury | +0.236 |
| sun_mercury | sun_saturn | +0.198 |
| moon_mars | moon_mercury | +0.164 |
| sun_mercury | moon_mercury | +0.113 |
| sun_moon | sun_mercury | +0.112 |
| sun_moon | moon_mars | +0.094 |
| sun_jupiter | jupiter_saturn | +0.088 |

### 2026

| Pair A | Pair B | r |
|---|---|---:|
| sun_moon | moon_mercury | +0.379 |
| sun_mercury | sun_venus | +0.263 |
| sun_mars | sun_jupiter | +0.244 |
| moon_mars | moon_jupiter | +0.233 |
| sun_mercury | sun_jupiter | +0.233 |
| moon_mercury | moon_jupiter | +0.153 |
| sun_moon | moon_jupiter | +0.135 |
| sun_moon | sun_mercury | +0.120 |
| sun_mercury | moon_mercury | +0.119 |
| sun_mars | sun_venus | -0.098 |

## Mercury-pair × non-Mercury-pair correlations, by year

### sun_mercury

| Other pair | 2024 | 2025 | 2026 |
|---|---:|---:|---:|
| sun_moon | +0.119 | +0.112 | +0.120 |
| sun_mars | +0.169 | +0.236 | +0.031 |
| sun_venus | +0.337 | +0.274 | +0.263 |
| sun_jupiter | +0.116 | +0.076 | +0.233 |
| sun_saturn | +0.053 | +0.198 | +0.072 |
| moon_mars | -0.016 | +0.002 | -0.024 |
| moon_jupiter | +0.005 | -0.014 | +0.007 |
| jupiter_saturn | +0.033 | +0.038 | -0.038 |

### moon_mercury

| Other pair | 2024 | 2025 | 2026 |
|---|---:|---:|---:|
| sun_moon | +0.350 | +0.351 | +0.379 |
| sun_mars | +0.024 | +0.019 | +0.003 |
| sun_venus | +0.054 | +0.034 | +0.060 |
| sun_jupiter | +0.007 | -0.003 | +0.034 |
| sun_saturn | -0.000 | +0.011 | -0.009 |
| moon_mars | +0.095 | +0.164 | +0.002 |
| moon_jupiter | +0.036 | +0.024 | +0.153 |
| jupiter_saturn | +0.012 | -0.000 | -0.012 |

## Caveats

- 2026 is a partial year (May–Dec only, 34,128 timestamps vs ~52,560 for full years). Sample size affects correlation estimate variance.

- Mode-decomposition `mode_ratio` time series have substantial within-year autocorrelation; pair-pair correlations should be interpreted as long-window summaries, not as independent-sample statistics.

- Three years is too few to cover synodic cycles between the slower grahas (Jupiter ≈12 yr, Saturn ≈29.5 yr). The pattern of pair-pair coupling can shift across years for reasons that are deterministic from the ephemeris.

- This document reports values without interpretation. Whether Mercury appears as a stable mediator across years, or whether the role wanders, is for the reader to judge from the tables and plots.
