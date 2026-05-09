# Mode-decomposition exploratory plots — Sun-Moon at Gainesville lagna, 2025

**Status:** exploratory visualization, NOT pre-registered. No statistical
tests are performed. The intent is to look at what the versor-aware engine
exposes — i.e., the magnetic-mode (|Re(Z_k)|) and dielectric-mode (|Im(Z_k)|)
components — across calendar 2025 at the Gainesville lagna, and ask: do the
two modes have different temporal structure, regimes, or relationships to
panchanga state?

This document describes what each plot is. Look at the plots fresh and
draw your own observations.

## Dataset

`sun_moon_modes_2025.parquet` — 52,560 rows at 10-min cadence. Columns:
`timestamp`, `sun_long`, `moon_long`, `lagna_long`, panchanga columns from
the canonical grid (`tithi_num`, `nakshatra_num`, `paksha`, `gandanta_flag`,
etc.), and per-k + composite mode-decomposition fields:
`magnetic_k{1,2,3,4,6,7,12}`, `dielectric_k{...}`, `mode_ratio_k{...}`,
`composite_magnetic`, `composite_dielectric`, `composite_mode_ratio`,
`mode_phase_angle = atan2(dielectric, magnetic) ∈ [0, π/2]`.

Headline distribution: composite_mode_ratio mean = 0.4977,
std = 0.1093, range [0.0002, 0.7504].

## Plots

### Time series
- **magnetic_dielectric_timeseries.png** — both modes plotted across 2025.
- **magnetic_dielectric_timeseries_january.png** — January zoom for fine structure.
- **mode_ratio_timeseries.png** — composite_mode_ratio across the year, with
  ekadashi tithis (11th) marked as orange dashed verticals.

### Distributions across panchanga state
- **mode_ratio_by_tithi.png** — boxplot grouped by tithi 1-30.
- **mode_ratio_by_nakshatra.png** — boxplot grouped by nakshatra 1-27.
- **mode_ratio_paksha_comparison.png** — overlaid histograms for
  śukla vs kṛṣṇa paksha.
- **mode_ratio_gandanta_vs_normal.png** — density overlay at gandanta moments
  vs non-gandanta.

### Per-k breakdown
- **magnetic_by_k.png** — small multiples, magnetic component for each k.
- **dielectric_by_k.png** — same for dielectric.
- **mode_ratio_by_k.png** — per-k mode ratio across 2025.

### Phase-space
- **magnetic_vs_dielectric_scatter.png** — (magnetic, dielectric) scatter,
  colored by tithi.
- **magnetic_vs_dielectric_by_paksha.png** — same, split into two panels
  by paksha.
- **polar_mode_phase.png** — polar plot. Theta = tithi (0-30 mapped to
  0-2π). r = mode_phase_angle = atan2(dielectric, magnetic). Orange = śukla,
  blue = kṛṣṇa.

### Spectrum
- **mode_ratio_spectrum.png** — FFT of composite_mode_ratio time series.
  Periods marked: synodic 29.53d, sidereal 27.32d, 1 day, 12h (M2 tidal),
  1 year.

## Caveat

The Sun-Moon pair-magnitude `|Z_k|` at any target reduces to
`2|cos(k(moon-sun)/2)|` by closed-form identity (target-invariant).
The mode decomposition into Re/Im is what carries target-dependent
information. These plots therefore reflect the lagna-coupled component
geometry, not the pair-magnitude (which is a global Sun-Moon function).
Anything appearing in these plots that varies systematically with
panchanga state is a candidate phenomenon for follow-up pre-registered
testing.
