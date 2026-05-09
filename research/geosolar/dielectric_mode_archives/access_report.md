# Pre-flight access report — atmospheric-electric circuit data archives

_Run: 2026-05-08_ · pilot fetches saved to `pilot_fetches/`

**Status: not pre-registered, no analysis run.** This is a verification pass
on whether the deep-research-report's suggested archives are actually
accessible and the data is in usable form for future PREREG_003 design.

## Headline

**2 of 3 target archives have a workable public-access path; 1 has only
partial sample data publicly available**, with the full record requiring
institutional contact.

| Archive | Public access | Format | Pilot fetch | Quality verdict |
|---|---|---|---|---|
| (A) Schumann resonance | partial | various | Zenodo 4276361 (monthly-diurnal averages, 7.8 KB) | not full-time-series; needs upgrade |
| (B) Atmospheric electric PG | YES | TSV | PANGAEA 942036 (Hungary 1962-2009, 41 MB, hourly) | excellent — 48 years, no auth |
| (C) Ionospheric potential | indirect | n/a | n/a | reconstructable from AEF + thunderstorm models |

## A. Schumann resonance

### A.1 Hylaty (Bieszczady Mountains, Poland) — operated by Jagiellonian University

- **URL/API:** none publicly listed. Station referenced in Kulak 2014 (Radio
  Science) and Acta Geophysica 2016, but no data download portal surfaced.
- **Authentication:** would require institutional contact (Jagiellonian U.,
  ELF group).
- **Data format:** unknown (research-grade time series, broadband ELF).
- **Sampling:** continuous, ~1 kHz raw, with derived SR fundamental + harmonic
  amplitude time series typically at 1-min resolution.
- **Coverage:** 2004–present (extended frequency range up to 300 Hz from 2013).
- **Sample fetch:** none — no public endpoint.
- **Verdict:** **inaccessible without institutional contact.**

### A.2 Mitzpe Ramon (Negev Desert, Israel) — Tel Aviv University

- **URL/API:** none publicly listed.
- **Authentication:** would require contact with TAU Department of Geophysics
  and Planetary Sciences.
- **Data format:** raw 5-min files at 250 Hz sampling on N-S, E-W magnetic
  components + vertical electric ball antenna, 50 Hz notch filter.
- **Coverage:** ~1999–present (multiple papers cite it).
- **Sample fetch:** none.
- **Verdict:** **inaccessible without institutional contact.**

### A.3 Mikhnevo (Russia) — Sadovsky Institute of Geosphere Dynamics

- **URL listed in literature:** `https://idg5.chph.ras.ru/geospheres-dynamics/schumann_resonances/`
- **Pilot fetch result:** **ECONNREFUSED** today — server unreachable. Possibly
  geo-blocked or temporarily offline. Not pursued further (would be sole
  alternative if Polish/Israeli archives also closed).
- **Verdict:** **unreliable** — inaccessible from this environment.

### A.4 Zenodo 4276361 — Williams et al. multi-station SR data

- **DOI:** [10.5281/zenodo.4276361](https://zenodo.org/records/4276361)
- **URL:** `https://zenodo.org/records/4276361`
- **Authentication:** none — public open access (CC-BY).
- **Files (10):** ALB_HEW.txt, ALB_HNS.txt, BOU_HEW.txt, BOU_HNS.txt,
  ESK_HNS.txt, HRN_HEW.txt, HRN_HNS.txt, NCK_EZ.txt, RI_HEW.txt, RI_HNS.txt
  (~43 KB each, total 267 KB).
- **Stations:** Alberta, Boulder Creek, Eskdalemuir, Hornsund, Nagycenk,
  Rhode Island.
- **Format:** plain TSV. **Not full time series — only monthly-averaged
  diurnal amplitude profiles** (24 hours × N months).
- **Time coverage:** mostly 2013-2016; Rhode Island Apr 1996-1997; Nagycenk
  Jan 1996 – Dec 1999.
- **Pilot fetch:** `pilot_fetches/Zenodo_4276361_NCK_EZ_schumann_nagycenk.txt`
  (7.8 KB — Nagycenk EZ component, 24 hours × 48 months 1996-1999).
- **Citation:** Williams et al. (Earth & Planetary Science Letters; multi-paper).
- **Verdict:** **partial** — useful for diurnal-pattern comparison, but
  **not a multi-decade time series**. Cannot run high-cadence wave-field
  cross-correlation against this directly.

### A.5 Other Zenodo SR datasets noted

- Sierra Nevada ELF station (Spain) raw 4-year (2013-2017) data on Zenodo —
  may have higher-cadence content; flagged for follow-up if SR becomes a
  PREREG_003 target.
- Mikhnevo software (Zenodo 6378370): full Python pipeline for SR calculation
  from raw magnetic field data. Code, not data.

## B. Atmospheric electric field / Carnegie curve

### B.1 Swider (Otwock-Świder, Poland) — Polish Academy of Sciences

- **URL:** `https://dataspace.atmospheric-electricity-net.eu/node/127`
- **Authentication:** required for data access — contact Marek Kubicki at
  IGF PAN, Warsaw. Page is a station metadata registry, not a data portal.
- **Variables advertised:** PG (since 1995), Jz air-earth current density
  (since 1985), CCN (since 1977), air conductivity (since 1958), meteorology
  (since 1977), pollution, radioactivity. **Air conductivity → 68 years!**
- **Time resolution:** 1 min to 10,000 min.
- **Pilot fetch:** none — not publicly downloadable.
- **Verdict:** **inaccessible without institutional contact.** A valuable
  archive but blocked behind email.

### B.2 PANGAEA 942036 — Széchenyi István Geophysical Observatory, Hungary

- **DOI:** [10.1594/PANGAEA.942036](https://doi.pangaea.de/10.1594/PANGAEA.942036)
- **URL (direct download):**
  `https://doi.pangaea.de/10.1594/PANGAEA.942036?format=textfile`
- **Authentication:** none — PANGAEA is a CC-BY open data repository.
- **Format:** tab-separated text with descriptive header (PANGAEA standard).
  Header section terminated by `*/`. 24 columns:
  Date/Time, PG uncorrected, PG corrected, PG corrected uncertainty,
  Temp/RH/wind/etc. (Campbell on-site after 2000), and ERA5 reanalysis
  meteorology back to 1962. All in V/m, °C, etc. — SI units throughout.
- **Sampling:** **hourly** averages.
- **Coverage:** **1962-01-01 to 2009-12-31** = 48 years, 420,768 rows.
- **Known issues (from dataset abstract):** tree-shielding bias dominates
  long-term trends in uncorrected PG; corrected series is provided but
  has a documented uncertainty from imprecise tree growth-rate priors.
  Hourly averages included only when ≥30 min of valid sub-hour data
  present.
- **Pilot fetch:** `pilot_fetches/PANGAEA_942036_szechenyi_hungary_PG_1962_2009.tab`
  — 41 MB, 420,817 lines (incl. header). Full record, no truncation.
  Per-year coverage plot at `pilot_fetches/plot_pangaea_hungary_PG_coverage.png`
  shows continuous record with mid-1960s and post-2005 noticeable degradation
  (PG col falls below 8760/yr).
- **Citation requirement:** "Always quote citation above when using data!"
  Full citation: Buzás, Szabóné André, Bór (2022), DOI 10.1594/PANGAEA.942036.
- **Volume estimate for full archive:** already at 41 MB for 48 years hourly
  + 22 covariates. Trivial. Single download.
- **Verdict:** **excellent — workable for PREREG_003.** Multi-decade hourly
  PG with ERA5 covariates, no auth, no rate limit, single 41MB file.

### B.3 Lerwick (Shetland, UK) 1964-1984 — Geoscience Data Journal 2025

- Surfaced via search: Harrison 2025 (Geoscience Data Journal). Hourly PG.
  Not pilot-fetched in this run (PANGAEA Hungary is sufficient as one
  representative AEF archive). Flagged for follow-up.

### B.4 ATMEL2007A multi-station archive (Tartu)

- URL: `http://ael.physic.ut.ee/tammet/dd/`
- Pilot fetch: **WebFetch timed out** at 60s. Server slow or unreachable
  briefly during this run.
- Per literature it includes hourly PG from 13 stations including 7
  former World Data Centre sites + the historical Carnegie vessel.
- Worth retrying in a future session.

### B.5 Mauna Loa (NOAA GML)

- Searched NOAA Global Monitoring Laboratory pages — **no AEF / PG
  measurement program surfaced**. Mauna Loa hosts CO2, aerosols, met,
  but the deep-research-report's mention of MLO AEF appears speculative
  / not borne out by NOAA's public data offerings.

## C. Ionospheric potential

Per spec, no direct fetch attempted. Notes for future PREREG_003 design:

- Ionospheric potential is rarely measured directly (would require balloon
  / sounding rocket). It is **reconstructed** from:
  1. Global PG measurements at stations (Carnegie-curve calculation),
  2. OTD/LIS lightning observations (proxy for global thunderstorm activity),
  3. Atmospheric conductivity profiles + global circuit modeling (Markson,
     Rycroft, Mareev, Tinsley frameworks).
- Modeled time series have been published (e.g. Mareev's framework, Williams
  & Sátori reconstructions).
- For PREREG_003: would be derived rather than fetched. Would treat the
  PANGAEA Hungary PG (above) as the proxy for ionospheric potential under
  fair-weather conditions, with known caveats about local vs global signal
  attribution.

## Pilot fetches saved

```
pilot_fetches/
  PANGAEA_942036_szechenyi_hungary_PG_1962_2009.tab    41.0 MB   ★
  Zenodo_4276361_NCK_EZ_schumann_nagycenk.txt           7.8 KB   ◐
  plot_pangaea_hungary_PG_jan1980.png                            ★
  plot_pangaea_hungary_PG_coverage.png                           ★
  plot_zenodo_nagycenk_schumann.png                              ◐
  plot_samples.py
```

★ = full multi-decade record obtained · ◐ = partial sample only

## Implications for future PREREG_003 design

The **dielectric-register physical observable** that's most accessible at
multi-decade resolution and cleanest to interpret is the **atmospheric
electric potential gradient** — and the PANGAEA Hungarian record
(1962-2009, hourly, with ERA5 covariates) is the ready-to-use primary
archive. A pre-registered test of Atlas's wave-field state vs PG could
be designed and locked tonight if desired; the data is already on disk.

The **Schumann resonance side** is harder. Multi-decade SR time series
require institutional contact with Jagiellonian (Hylaty) or TAU (Mitzpe
Ramon). The Zenodo monthly-diurnal averages would only support
diurnal-pattern comparisons, not the full-cadence wave-field correlation.

**If PREREG_003 is to test against both PG and SR**, it needs an institutional
data-request step before the design can be locked. **If PG alone is sufficient**
(the dielectric register is well-represented by PG), the design can proceed
on the existing PANGAEA fetch immediately.

## Sources

- [PANGAEA 942036 — Hungary PG 1962-2009](https://doi.pangaea.de/10.1594/PANGAEA.942036)
- [Atmospheric Electricity Network (Swider entry)](https://dataspace.atmospheric-electricity-net.eu/node/127)
- [Zenodo 4276361 — Williams et al. SR data](https://zenodo.org/records/4276361)
- [Hylaty station — Kulak et al. 2014 Radio Science](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014RS005400)
- [Hylaty 10-year analysis — Acta Geophysica 2016](https://link.springer.com/article/10.1515/acgeo-2016-0101)
- [Mitzpe Ramon SR (TAU) — Pechony 2007 Radio Science](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2006RS003456)
- [Lerwick 1964-1984 PG — Harrison 2025 GDJ](https://rmets.onlinelibrary.wiley.com/doi/10.1002/gdj3.70009)
- [GloCAEM atmospheric electricity network](https://www.sciencedirect.com/science/article/pii/S1364682618304541)
- [Mikhnevo SR software — Zenodo 6378370](https://doi.org/10.5281/zenodo.6378370)
- [ATMEL2007A archive (Tartu, ut.ee)](http://ael.physic.ut.ee/tammet/dd/)
