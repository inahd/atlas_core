# datasets/geosolar/

Geosolar field data for Atlas. Two distinct stores live here: a **live log** populated by the running kernel, and an **archive** of historical records pulled from public archives for retrospective analysis.

## Live log — `kp_log.csv`

Produced by `npu_engine/field/geosolar_engine.py::log_geosolar_state`. The background thread (`_start_geosolar_logger`, default `interval_s=600`) appends one row every ~10 minutes (observed cadence: median 602 s, drift due to fetch latency).

**16 columns** (header row + data):

```
datetime, kp, kp_class, solar_wind_speed, solar_wind_bz,
flare_class, flare_active, xray_flux, seismic_count, max_magnitude,
field_modifier, tithi, nakshatra, hora, vara, paksha
```

The first 11 columns are physical (NOAA SWPC + USGS); the last 5 are panchanga state passed in at write time. `field_modifier` is a weighted normalized scalar over the five physical inputs (Kp, X-ray flux, wind speed, southward Bz, max seismic magnitude) — see `geosolar_engine.py:232-253`. It does **not** depend on panchanga, so panchanga ↔ field_modifier correlation tests are not circular.

Do not edit `kp_log.csv` by hand; the running kernel appends to it.

## Archive — `archive/`

Multi-decade historical records, one subdirectory per source. **Panchanga columns are not stored here** — they are joined retrospectively at query time from `npu_engine/jyotisha_engine.py` (Swiss Ephemeris) for whatever timestamp range the analysis needs.

| dir | source | URL | earliest | cadence |
|---|---|---|---|---|
| `kp/`           | GFZ Potsdam definitive Kp + ap                   | `https://datapub.gfz-potsdam.de/download/10.5880.Kp.0001/Kp_definitive/` (200 OK, HTML index) and NOAA mirror `https://services.swpc.noaa.gov/text/daily-geomagnetic-indices.txt` (200 OK, text/plain) | 1932 | 3-h |
| `dst/`          | Kyoto WDC Dst index                              | `https://wdc.kugi.kyoto-u.ac.jp/dstdir/` (200 OK, HTML portal) | 1957 | 1-h |
| `solar_wind/`   | DSCOVR / ACE solar wind speed + IMF Bz           | NOAA SWPC current `services.swpc.noaa.gov/products/solar-wind/` ; full archive `ngdc.noaa.gov/dscovr/` and `cdaweb.gsfc.nasa.gov/` for ACE | ACE: 1997-08-25 ; DSCOVR: 2015-06-08 | 1-min |
| `xray/`         | GOES X-ray flux (XRS A/B)                        | NOAA NCEI `https://www.ncei.noaa.gov/data/goes-space-environment-monitor/access/` | ~1986 | 1-min |
| `seismic/`      | USGS ANSS ComCat earthquake catalog              | `https://earthquake.usgs.gov/fdsnws/event/1/query` (200 OK, text/csv) | comprehensive 1973+ | event-driven |
| `tide/`         | NOAA CO-OPS — single reference station           | `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter` (200 OK, text/comma-separated-values) | per-station; SF (9414290) 1854 | 6-min / hourly |

Solar wind and X-ray are listed deferred; bulk pulls for those will follow the Kp/Dst/seismic/tide first wave.

## Update strategy

- **One-time bulk fetch** to populate each archive subdir from the source's earliest available date through "now − 1 month" (definitive cutoff).
- **Weekly append job** to be added later — pulls only the new records since last run, appends to the existing file. Job script not yet written; planned location `npu_engine/field/geosolar_archive_sync.py` (or similar). Until that exists, archive stays at whatever the bulk fetch produced.

## File-format convention

- **Archive files: Parquet.** Column-typed, compressed, fast to slice by date. Default engine: `pyarrow`. One file per source per decade (e.g. `archive/kp/kp_1932_1949.parquet`, `archive/kp/kp_1950_1969.parquet`, …) so individual files stay under ~50 MB and a single decade reload doesn't require rewriting the whole archive.
- **Live log: CSV.** Preserved as-is for compatibility with the running kernel's `csv.writer` append path. Conversion to Parquet happens only at retrospective-analysis time, not at write time.
- **No mixed schemas across files within one source.** A schema bump (added column, renamed column) starts a new directory: `archive/kp/v2/`.

## Known issues in the live log

- `kp_log.csv` contains one corrupted row at byte offset 91987 (122 NUL bytes from an interrupted write). 1683/1684 rows parse cleanly. Skip rows whose `datetime` doesn't ISO-parse.
- `hora` column is empty from row 2 onward — the panchanga payload's hora field stopped being populated after the first row. Not a data-loss issue per se (hora is computable from `datetime` + `vara`), just an inconsistency.
- 47 gaps > 15 min in the log so far (kernel pauses, network outages). Gaps don't corrupt the file; rows on either side parse normally.
