# Multi-pair mode-phase dataset, 2026 (partial year: 2026-05-09 00:00 UTC through 2026-12-31 23:50 UTC, since today is 2026-05-08)

10-min cadence Sun-Moon, Sun-Mars, Sun-Mercury, Sun-Venus, Sun-Jupiter,
Sun-Saturn, Moon-Mars, Moon-Mercury, Moon-Jupiter, Jupiter-Saturn pair
versor decomposition at the Gainesville lagna (lat=29.65, lon=-82.34).

- Rows: **34,128**
- Columns: 204 (per-pair re_k/im_k for k∈{1,2,3,4,6,7,12}, magnetic,
  dielectric, mode_ratio, mode_phase, synodic_phase, plus base
  panchanga columns)
- Generated using `npu_engine.jyotisha_engine.compute_pair_interference`
  (post-DEVIATION_001 versor-aware engine).

Cross-year comparison plots and synthesis live at
`research/geosolar/exploratory/mode_phase_multi_year_comparison/`.

This dataset is exploratory. NOT pre-registered.
