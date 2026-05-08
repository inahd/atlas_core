# BULK_REPORT_1973_2024 — geosolar archive bulk fetch

_Run: 2026-05-08T17:59:58+00:00 · wall-clock 14.2 min_

Coverage: **1973-01-01 .. 2024-12-31**. 2025 data is in the pilot files (`kp_2025.parquet`, `dst_2025.parquet`, `seismic_2025_M4plus.parquet`, `tide_sf_2025_hourly.parquet`); merge at analysis time. Decade partitioning uses fixed boundaries (1970s = 1973–1979 partial; 2020s = 2020–2024 partial; all others full 10-year decades).

## Footprint

Total disk: **33,686,267 bytes** (32.1 MB) across the 24 decade Parquet files.

## kp

- HTTP requests: **1**
- years OK: **0** / 52
- years failed: **0**
- rows total: **0**
- rows skipped (malformed): 0

| decade | rows | bytes | path |
|---|---:|---:|---|
| 1970s | 20,448 | 220,894 | `datasets/geosolar/archive/kp/kp_1970s.parquet` |
| 1980s | 29,224 | 313,573 | `datasets/geosolar/archive/kp/kp_1980s.parquet` |
| 1990s | 29,216 | 313,806 | `datasets/geosolar/archive/kp/kp_1990s.parquet` |
| 2000s | 29,224 | 314,064 | `datasets/geosolar/archive/kp/kp_2000s.parquet` |
| 2010s | 29,216 | 313,425 | `datasets/geosolar/archive/kp/kp_2010s.parquet` |
| 2020s | 14,616 | 156,013 | `datasets/geosolar/archive/kp/kp_2020s.parquet` |

## dst

- HTTP requests: **493**
- years OK: **37** / 52
- years failed: **0**
- rows total: **324,336**
- rows skipped (malformed): 0
- date range: 1973-01-01 00:00:00+00:00  →  2009-12-31 23:00:00+00:00
- Dst cutoffs: {'final': (1957, 2020), 'provisional': (2021, 1, 2025, 6)}

| decade | rows | bytes | path |
|---|---:|---:|---|
| 1970s | 61,344 | 626,220 | `datasets/geosolar/archive/dst/dst_1970s.parquet` |
| 1980s | 87,672 | 907,303 | `datasets/geosolar/archive/dst/dst_1980s.parquet` |
| 1990s | 87,648 | 909,500 | `datasets/geosolar/archive/dst/dst_1990s.parquet` |
| 2000s | 87,672 | 909,707 | `datasets/geosolar/archive/dst/dst_2000s.parquet` |
| 2010s | 87,648 | 896,240 | `datasets/geosolar/archive/dst/dst_2010s.parquet` |
| 2020s | 43,848 | 446,015 | `datasets/geosolar/archive/dst/dst_2020s.parquet` |

## seismic

- HTTP requests: **0**
- years OK: **0** / 52
- years failed: **0**
- rows total: **0**
- rows skipped (malformed): 0

| decade | rows | bytes | path |
|---|---:|---:|---|
| 1970s | 29,473 | 1,317,215 | `datasets/geosolar/archive/seismic/seismic_1970s_M4plus.parquet` |
| 1980s | 53,669 | 2,378,508 | `datasets/geosolar/archive/seismic/seismic_1980s_M4plus.parquet` |
| 1990s | 76,861 | 3,355,452 | `datasets/geosolar/archive/seismic/seismic_1990s_M4plus.parquet` |
| 2000s | 118,923 | 4,932,519 | `datasets/geosolar/archive/seismic/seismic_2000s_M4plus.parquet` |
| 2010s | 144,133 | 6,559,426 | `datasets/geosolar/archive/seismic/seismic_2010s_M4plus.parquet` |
| 2020s | 77,420 | 3,755,520 | `datasets/geosolar/archive/seismic/seismic_2020s_M4plus.parquet` |

**Magnitude bins per decade:**

| decade | M4.0-4.9 | M5.0-5.9 | M6.0-6.9 | M7.0+ |
|---|---:|---:|---:|---:|
| 1970s | 18,321 | 10,452 | 622 | 78 |
| 1980s | 37,644 | 14,738 | 1,177 | 110 |
| 1990s | 62,201 | 13,125 | 1,381 | 154 |
| 2000s | 101,688 | 15,649 | 1,442 | 143 |
| 2010s | 125,664 | 16,975 | 1,334 | 160 |
| 2020s | 68,730 | 8,039 | 583 | 68 |

## tide

- HTTP requests: **0**
- years OK: **0** / 52
- years failed: **0**
- rows total: **0**
- rows skipped (malformed): 0

| decade | rows | bytes | path |
|---|---:|---:|---|
| 1970s | 59,687 | 621,143 | `datasets/geosolar/archive/tide/tide_sf_1970s_hourly.parquet` |
| 1980s | 87,672 | 924,990 | `datasets/geosolar/archive/tide/tide_sf_1980s_hourly.parquet` |
| 1990s | 87,640 | 979,405 | `datasets/geosolar/archive/tide/tide_sf_1990s_hourly.parquet` |
| 2000s | 87,671 | 1,039,642 | `datasets/geosolar/archive/tide/tide_sf_2000s_hourly.parquet` |
| 2010s | 87,096 | 1,030,749 | `datasets/geosolar/archive/tide/tide_sf_2010s_hourly.parquet` |
| 2020s | 38,904 | 464,938 | `datasets/geosolar/archive/tide/tide_sf_2020s_hourly.parquet` |

## Degraded coverage summary

None — all decades within tolerance for their nominal expected row counts.
