# PREREG_006 EXECUTION RESULT — multi-station Schumann replication

**Lock-marker:** 62328de (verified before execution).
**Outcome category per prereg §4:** **4c**

Date: 2026-05-08

## Lock verification

- `git log --follow research/geosolar/preregistrations/PREREG_006_*.md` shows
  62328de as the only commit on the prereg path before this execution session.
- File sha256 at lock-time: `bea01f6e0f84fdee4ad5faf29dd285acbf3a0ef9edc0b1284c288ec79363378c`

## Process notes (declared, not deviations)

- Williams files have heterogeneous cadence: 4 stations are 10-minute resolution
  (ALB, BOU, ESK, HRN, 144 rows × N month-year cols); RI is hourly (24 rows ×
  N cols). Per-prereg unit-of-analysis `(station, month, hour)` interpreted as
  hour-of-day; 10-min files aggregated to per-hour means before analysis.
- BOU is HNS-only on Zenodo (BOU_HEW.txt absent); handled per prereg §3.2
  asymmetric-components rule (use available component).
- ALB component files have units [pT²/Hz] (power spectral density, not pure amplitude).
  All per-station regressions are within-station so absolute units do not matter
  for the test; the combined-stations regression carries station fixed-effects
  which absorb cross-station unit differences.
- Fetch failures: none

## Per-station results

Per prereg §3.4, OLS per station:
`amplitude ~ envelope_c + mode_ratio_c + envelope_c × mode_ratio_c + hour_FE + month_FE`

Block-bootstrap CI: 60-record blocks, 1,000 resamples, seed default_rng(20260508).

| Station | n | β_mr | 95% CI on β_mr | passes (CI_hi<0)? | β_interaction | OLS p_int |
|---|---:|---:|---|:-:|---:|---:|
| ALB | 1,152 | +0.0139 | [-0.0248, +0.0456] | · | +0.0209 | 0.742 |
| BOU | 1,152 | +0.0166 | [-0.0351, +0.0699] | · | +0.1397 | 0.163 |
| ESK | 1,152 | +0.0010 | [-0.0077, +0.0110] | · | +0.0208 | 0.215 |
| HRN | 1,152 | +0.0076 | [-0.0490, +0.0659] | · | +0.1667 | 0.0115 |
| RI | 48 | -1.3109 | [+nan, +nan] | · | -5.0019 | 0.206 |

Stations passing one-tailed-negative criterion: **0 of 5**.

## Combined-stations regression

Per prereg §3.4, pooled with station FE + station × hour interaction:

    sr_amplitude ~ envelope_c + mode_ratio_c + envelope_c × mode_ratio_c
                  + station + hour_FE + month_FE + station × hour

- n = 4,656, parameters = 134, R² = 0.98741
- β_mode_ratio   = +0.00172,  SE = 0.01240,
  OLS p = 0.89,  bootstrap 95% CI = [-0.01741, +0.02862]
- β_interaction  = +0.07856,  SE = 0.03905,
  OLS p = 0.0443,  bootstrap 95% CI = [-0.00002, +0.17221]

## Survival criteria (per prereg §3.6, locked)

| # | Criterion | Result |
|---|---|:-:|
| 1 | Combined β_mode_ratio bootstrap CI excludes zero | **FAIL** |
| 2 | Sign matches AEF prior (negative) | **FAIL** |
| 3 | ≥ 3 of 5 stations individually pass with same sign | **FAIL** (0/5) |
| 4 | Combined β_interaction bootstrap CI includes zero | **PASS** |

## Outcome category (locked interpretations)

**Category 4c**

Pooled null. The Hungary AEF mode_ratio main effect does not replicate to multi-station Schumann data. The dielectric-register coupling claim is not supported beyond the single-location AEF exploratory result.

## Plots

- `plots/mode_ratio_vs_amplitude_per_station.png` — 5 panels, scatter + per-station β line.
- `plots/per_station_beta_mode_ratio_with_CI.png` — forest plot.
- `plots/combined_regression_diagnostic.png` — residuals vs fitted, residual histogram.
- `plots/sign_consistency_check.png` — per-station β_mr with combined overlay; pass/fail color-coded.

## Files

- `data/` — fetched Williams Zenodo 4276361 station files (raw .txt).
- `combined_records.parquet` — long-form (station, year, month, hour) records with mode_ratio, envelope, amplitude.
- `per_station_results.parquet` — per-station regression outputs.
- `combined_summary.json` — combined regression coefficients + bootstrap CIs.
- `run_schumann_replication.py` — execution script.

*Total wall: 65.0s*