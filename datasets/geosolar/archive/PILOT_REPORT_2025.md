# PILOT_REPORT_2025 — geosolar archive validation

Run timestamp: 2026-05-08T16:37:29+00:00

## kp

- output: `datasets/geosolar/archive/kp/kp_2025.parquet`
- file size: 32,739 bytes
- HTTP requests: 1
- rows fetched: 2,920
- rows skipped (malformed): 0
- date range: 2025-01-01 00:00:00+00:00  →  2025-12-31 21:00:00+00:00
- gaps > 1 day: none

**Sample rows (round-trip read from Parquet):**

```
                timestamp  kp    ap
2025-01-01 00:00:00+00:00 4.0  27.0
2025-01-01 03:00:00+00:00 5.3  56.0
2025-01-01 06:00:00+00:00 5.0  48.0
2025-01-01 09:00:00+00:00 6.0  80.0
2025-01-01 12:00:00+00:00 6.7 111.0
```

## dst

- output: `datasets/geosolar/archive/dst/dst_2025.parquet`
- file size: 90,193 bytes
- HTTP requests: 12
- rows fetched: 8,760
- rows skipped (malformed): 0
- date range: 2025-01-01 00:00:00+00:00  →  2025-12-31 23:00:00+00:00
- gaps > 1 day: none

**Sample rows (round-trip read from Parquet):**

```
                timestamp  dst_nT
2025-01-01 00:00:00+00:00   -26.0
2025-01-01 01:00:00+00:00   -30.0
2025-01-01 02:00:00+00:00   -30.0
2025-01-01 03:00:00+00:00   -29.0
2025-01-01 04:00:00+00:00   -22.0
```

## seismic

- output: `datasets/geosolar/archive/seismic/seismic_2025_M4plus.parquet`
- file size: 869,705 bytes
- HTTP requests: 1
- rows fetched: 18,303
- rows skipped (malformed): 0
- date range: 2025-01-01 00:13:22.650000+00:00  →  2025-12-31 23:52:11.327000+00:00
- gaps > 1 day: none
- magnitude bin counts:
    - M4.0-4.9: 16,174
    - M5.0-5.9: 1,984
    - M6.0-6.9: 129
    - M7.0+: 16

**Sample rows (round-trip read from Parquet):**

```
                       timestamp  latitude  longitude   depth_km  magnitude magType                                 place   event_id
2025-01-01 00:13:22.650000+00:00   12.7441   143.6244  35.000000        4.2      mb    127 km WSW of Merizo Village, Guam us6000pjr6
2025-01-01 01:00:50.839000+00:00   34.6287    16.5823  10.000000        4.0      mb        228 km SE of Marsaskala, Malta us6000pgrt
2025-01-01 01:07:10.492000+00:00   -5.9077   128.8869 277.355011        4.4      mb        256 km SSE of Ambon, Indonesia us6000pgru
2025-01-01 01:46:59.538000+00:00   -3.8682   151.6536  10.000000        4.7      mb 67 km WNW of Rabaul, Papua New Guinea us6000pjqz
2025-01-01 02:00:06.918000+00:00   -3.8521   151.6207  10.000000        4.5      mb 71 km WNW of Rabaul, Papua New Guinea us6000pjr1
```

## tide

- output: `datasets/geosolar/archive/tide/tide_sf_2025_hourly.parquet`
- file size: 113,272 bytes
- HTTP requests: 1
- rows fetched: 8,760
- rows skipped (malformed): 0
- date range: 2025-01-01 00:00:00+00:00  →  2025-12-31 23:00:00+00:00
- gaps > 1 day: none

**Sample rows (round-trip read from Parquet):**

```
                timestamp  water_level_m station_id  sigma
2025-01-01 00:00:00+00:00          0.035    9414290  0.052
2025-01-01 01:00:00+00:00         -0.269    9414290  0.046
2025-01-01 02:00:00+00:00         -0.343    9414290  0.042
2025-01-01 03:00:00+00:00         -0.295    9414290  0.042
2025-01-01 04:00:00+00:00         -0.015    9414290  0.046
```
